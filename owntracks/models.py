from django.db import models
from django.utils.timezone import now


# Create your models here.

class OwnTrackLog(models.Model):
    tid = models.CharField(max_length=100, null=False, verbose_name='User')
    lat = models.FloatField(verbose_name='Latitude')
    lon = models.FloatField(verbose_name='Longitude')
    created_time = models.DateTimeField('Created at', default=now)

    def __str__(self):
        return self.tid

    class Meta:
        ordering = ['created_time']
        verbose_name = "OwnTrackLogs"
        verbose_name_plural = verbose_name
        get_latest_by = 'created_time'
