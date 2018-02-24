from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string


class Ticket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    program = models.ForeignKey('paikkala.Program', on_delete=models.PROTECT, related_name='tickets')
    ctime = models.DateTimeField(auto_now_add=True)
    zone = models.ForeignKey('paikkala.Zone', on_delete=models.CASCADE, related_name='tickets')
    row = models.ForeignKey('paikkala.Row', on_delete=models.CASCADE, related_name='tickets')
    number = models.IntegerField()
    key = models.CharField(max_length=8, unique=True)

    class Meta:
        unique_together = [
            ('program', 'zone', 'number'),
        ]

    def save(self, **kwargs):
        if not self.key:
            self.key = get_random_string(8, 'acdefghjklmqrtuvwxyz')
        return super().save(**kwargs)

    def __str__(self):
        return '{program} – {zone} – {number}'.format(
            program=self.program.name,
            zone=self.zone,
            number=self.number,
        )
