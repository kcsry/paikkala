from django.db import models


class SeatQualifier(models.Model):
    """
    Qualifies a range of seat numbers within a zone without affecting row assignment.

    E.g. "left" / "right" to divide seats within the floor space.
    """
    zone = models.ForeignKey('paikkala.Zone', related_name='seat_qualifiers', on_delete=models.CASCADE)
    start_number = models.IntegerField()
    end_number = models.IntegerField()
    text = models.CharField(max_length=64)

    def __str__(self):
        return 'Zone %s seats %d..%d qualified "%s"' % (self.zone, self.start_number, self.end_number, self.text)
