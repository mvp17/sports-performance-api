from django.urls import path
from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('settings', configuration, name='settings'),

    path('files', FileList.as_view(), name='file_list'),
    path('files/upload', UploadFile.as_view(), name='upload_file'),
    path('files/<int:pk>', delete_file, name= 'delete_file'),

    path('data_analytics', data_analytics, name='data analytics'),
    path('variable_selector', variable_selector, name='variable selector'),
    path('line_chart', line_chart, name='line chart'),
]
