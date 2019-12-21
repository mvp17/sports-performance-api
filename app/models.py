from django.db import models


class PerformanceData(models.Model):
    title = models.CharField(max_length=100)
    athlete = models.CharField(max_length=100)
    csv = models.FileField(upload_to='csv_files/')

    def __str__(self):
        return self.title
