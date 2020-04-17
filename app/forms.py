from django import forms
from .models import *


class FileForm(forms.ModelForm):
    class Meta:
        model = LoadData
        fields = ('title', 'athlete', 'csv', 'event_file', 'frequency')


class SettingsForm(forms.ModelForm):
    class Meta:
        model = ConfigurationSetting
        fields = ('init_time_ms', 'fin_time_ms', 'frequency')


class KeyWordsEventsForm(forms.ModelForm):
    class Meta:
        model = KeyWordEventsFile
        fields = ('time_ms_name', 'duration_time_ms_name', 'chart_perf_vars')


class KeyWordsDevicesForm(forms.ModelForm):
    class Meta:
        model = KeyWordDevicesFile
        fields = ('time_name',)
