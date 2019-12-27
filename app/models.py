from django.db import models


class PerformanceData(models.Model):
    title = models.CharField(max_length=100)
    athlete = models.CharField(max_length=100)
    csv = models.FileField(upload_to='csv_files/')
    init_time = models.TimeField(help_text="H:M:S")
    fin_time = models.TimeField(help_text="H:M:S")

    FREQ_1FS = "1 f/s"
    FREQ_5FS = "5 f/s"
    FREQ_10FS = "10 f/s"
    FREQ_25FS = "25 f/s"
    FREQ_CHOICES = [(FREQ_1FS, '1 f/s'),
                    (FREQ_5FS, '5 f/s'),
                    (FREQ_10FS, '10 f/s'),
                    (FREQ_25FS, '25 f/s')]
    frequency = models.CharField(max_length=10, choices=FREQ_CHOICES, unique=True, default=FREQ_5FS)

    def delete(self, *args, **kwargs):
        self.csv.delete()
        super().delete(*args, **kwargs)


class ConfigurationSettings(models.Model):
    init_frame = models.IntegerField(null=True, blank=True)
    fin_frame = models.IntegerField(null=True, blank=True)
    init_time = models.TimeField(help_text="H:M:S")
    fin_time = models.TimeField(help_text="H:M:S")

    FREQ_1FS = "1 f/s"
    FREQ_5FS = "5 f/s"
    FREQ_10FS = "10 f/s"
    FREQ_25FS = "25 f/s"
    FREQ_CHOICES = [(FREQ_1FS, '1 f/s'),
                    (FREQ_5FS, '5 f/s'),
                    (FREQ_10FS, '10 f/s'),
                    (FREQ_25FS, '25 f/s')]
    frequency = models.CharField(max_length=10, choices=FREQ_CHOICES, unique=True, default=FREQ_5FS)
