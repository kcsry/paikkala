import datetime
import random
from typing import Any, List, Optional

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.timezone import now


def generate_key() -> str:
    key = ''
    while len(key) < 8:
        char = random.choice('aaaiiioooeeecdfghjklmqrtuv')
        if key.endswith(char):
            continue
        key += char
    return key


class TicketQuerySet(models.QuerySet):
    def valid(self, at: Optional[datetime.datetime] = None) -> models.QuerySet:
        if not at:
            at = now()
        return self.filter(Q(program__invalid_after__isnull=True) | Q(program__invalid_after__gt=at))


class Ticket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    name = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    program = models.ForeignKey('paikkala.Program', on_delete=models.PROTECT, related_name='tickets')
    ctime = models.DateTimeField(auto_now_add=True)
    zone = models.ForeignKey('paikkala.Zone', on_delete=models.CASCADE, related_name='tickets')
    row = models.ForeignKey('paikkala.Row', on_delete=models.CASCADE, related_name='tickets')
    number = models.IntegerField()
    key = models.CharField(max_length=8, unique=True)
    qualifier_text_cache = models.TextField(editable=False, blank=True)
    objects = TicketQuerySet.as_manager()

    class Meta:
        unique_together = [
            ('program', 'zone', 'number'),
        ]

    def is_valid(self, at: Optional[datetime.datetime] = None) -> bool:
        if not at:
            at = now()
        if self.program.invalid_after and at > self.program.invalid_after:
            return False
        return True

    def save(self, **kwargs: Any) -> None:
        if not self.key:
            self.key = generate_key()
        if not self.pk:
            self.recompute_qualifiers()
        return super().save(**kwargs)

    def recompute_qualifiers(self) -> None:
        self.qualifier_text_cache = '\n'.join([
            q.text
            for q
            in self.zone.seat_qualifiers.filter(start_number__lte=self.number, end_number__gte=self.number)
        ])

    @property
    def qualifier_texts(self) -> List[str]:
        return self.qualifier_text_cache.splitlines() if self.qualifier_text_cache else []

    @property
    def qualified_zone(self) -> str:
        name = str(self.zone)
        if self.qualifier_texts:
            qualifiers = ' '.join(self.qualifier_texts)
            name = f'{name} {qualifiers}'
        return name

    def __str__(self) -> str:
        return f'{self.program.name} – {self.qualified_zone} – {self.number}'
