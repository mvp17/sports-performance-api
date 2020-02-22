from django.urls import path
from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('signup', signup, name='signup'),
    path('settings', Configuration.as_view(), name='settings'),

    path('files', FileList.as_view(), name='file_list'),
    path('files/upload', upload_csv_file, name='upload_file'),
    path('files/<int:pk>', delete_file, name='delete_file'),

    path('data_analytics', data_analytics, name='data analytics'),
]
