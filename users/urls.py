from django.urls import path

from . import views

urlpatterns = [
    path('login', views.LogIn.as_view(), name='login'),
]
