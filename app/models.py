from django.db import models


class LoadData(models.Model):
    title = models.CharField(max_length=100, blank=True)
    athlete = models.CharField(max_length=100, blank=True)
    csv = models.FileField(upload_to='csv_files/')

    CHOICES_BOOL = [(0, "Yes"), (1, "No")]
    event_file = models.IntegerField(blank=False, help_text="Is it events file what you are uploading?",
                                     choices=CHOICES_BOOL, default=0)

    FREQ_1FS = 1
    FREQ_5FS = 5
    FREQ_10FS = 10
    FREQ_25FS = 25
    FREQ_100FS = 100
    FREQ_1000FS = 1000
    FREQ_NONE = 0
    FREQ_CHOICES = [(FREQ_NONE, ""),
                    (FREQ_1FS, "1 Hz"),
                    (FREQ_5FS, "5 Hz"),
                    (FREQ_10FS, "10 Hz"),
                    (FREQ_25FS, "25 Hz"),
                    (FREQ_100FS, "100 Hz"),
                    (FREQ_1000FS, "1000 Hz")
                    ]
    frequency = models.IntegerField(choices=FREQ_CHOICES, default=FREQ_NONE,
                                    help_text="Ignore the field when uploading EVENTS file.")

    def delete(self, *args, **kwargs):
        self.csv.delete()
        super().delete(*args, **kwargs)


class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(SingletonModel, self).delete(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class ConfigurationSetting(SingletonModel):
    init_time_ms = models.PositiveIntegerField(null=True, blank=False, help_text="Time in milliseconds.")
    fin_time_ms = models.PositiveIntegerField(null=True, blank=False, help_text="Time in milliseconds.")

    FREQ_1FS = 1
    FREQ_5FS = 5
    FREQ_10FS = 10
    FREQ_25FS = 25
    FREQ_100FS = 100
    FREQ_1000FS = 1000
    FREQ_CHOICES = [(FREQ_1FS, "1 Hz"),
                    (FREQ_5FS, "5 Hz"),
                    (FREQ_10FS, "10 Hz"),
                    (FREQ_25FS, "25 Hz"),
                    (FREQ_100FS, "100 Hz"),
                    (FREQ_1000FS, "1000 Hz")
                    ]
    frequency = models.IntegerField(choices=FREQ_CHOICES, default=FREQ_5FS, help_text="Data table frequency.")


class KeyWordEventsFile(SingletonModel):
    time_ms_name = models.CharField(null=True, max_length=100, blank=False,
                                    help_text="Column name of Time in milli-seconds values.")
    duration_time_ms_name = models.CharField(null=True, max_length=100, blank=False,
                                             help_text="Column name of Time Duration in milli-seconds values.")
    chart_perf_vars = models.TextField(blank=True, max_length=250,
                                       help_text="Performance variables separated by comma for showing their data "
                                                 "to the chart data. Use white spaces if you like. "
                                                 "Please put the variables in the same order as they are shown."
                                       )


class KeyWordDevicesFile(SingletonModel):
    time_name = models.CharField(null=True, max_length=100, blank=False,
                                 help_text="Column name of Time of DEVICES files.")
