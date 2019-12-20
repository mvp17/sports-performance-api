from django.urls import path
from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('settings', settings, name='settings'),
    path('upload', upload, name='upload'),
    path('data_analytics', data_analytics, name='data analytics'),
    path('variable_selector', variable_selector, name='variable selector'),
    path('line_chart', line_chart, name='line chart'),
]
