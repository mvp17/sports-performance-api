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
