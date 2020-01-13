from .forms import *
from django.views.generic import *
from .models import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm


def home(request):
    return render(request, 'base.html')


class LogIn(LoginRequiredMixin, generic.CreateView):
    success_url = reverse_lazy('home')
    template_name = 'registration/login.html'


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })


class Configuration(CreateView):
    model = ConfigurationSettings
    form_class = SettingsForm
    success_url = reverse_lazy('home')
    template_name = 'settings.html'


def delete_file(request, pk):
    if request.method == 'POST':
        file = PerformanceData.objects.get(pk=pk)
        file.delete()
    return redirect('file_list')


class FileList(ListView):
    model = PerformanceData
    template_name = 'uploading/file_list.html'
    context_object_name = 'files'


def upload_csv_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        csv_file = request.FILES['csv']
        if form.is_valid() and csv_file.name.endswith('.csv'):
            form.save()
            return redirect('file_list')
        else:
            messages.error(request, 'Error in parameters (only csv files)')
    else:
        form = FileForm()
    return render(request, 'uploading/upload_file.html', {
        'form': form
    })


def data_analytics(request):
    return render(request, 'data_analytics.html')


def variable_selector(request):
    return render(request, 'variable_selector.html')


def line_chart(request):
    return render(request, 'line_chart.html')
