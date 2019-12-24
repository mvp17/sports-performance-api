from django import forms
from .models import *


class FileForm(forms.ModelForm):
    class Meta:
        model = PerformanceData
        fields = ('title', 'athlete', 'csv')


class SettingsForm(forms.ModelForm):
    class Meta:
        model = ConfigurationSettings
        fields = ('init_frame', 'fin_frame', 'init_time', 'fin_time', 'frequency')

