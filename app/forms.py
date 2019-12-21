from django import forms
from .models import PerformanceData


class FileForm(forms.ModelForm):
    class Meta:
        model = PerformanceData
        fields = ('title', 'athlete', 'csv')
