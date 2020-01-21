from django import forms
from .models import *


class FileForm(forms.ModelForm):
    class Meta:
        model = PerformanceData
        fields = ('title', 'athlete', 'csv', 'init_frame', 'fin_frame', 'frequency')


class SettingsForm(forms.ModelForm):
    class Meta:
        model = ConfigurationSettings
        fields = ('init_frame', 'fin_frame', 'frequency')

