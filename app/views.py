from django.shortcuts import render, redirect
from .forms import *
from django.views.generic import *
from django.urls import reverse_lazy
from .models import *
from django.contrib import messages


def home(request):
    return render(request, 'base.html')


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
    return render(request, 'line_chart.html ')
