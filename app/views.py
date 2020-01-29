import pandas as pd
# import jsonpickle

from .forms import *
from itertools import dropwhile
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
        file = LoadData.objects.get(pk=pk)
        file.delete()
    return redirect('file_list')


class FileList(ListView):
    model = LoadData
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


def get_max_freq(objects):
    frequency = 0
    for obj in objects:
        if obj.frequency > frequency:
            frequency = obj.frequency
    return frequency


def data_analytics(request):
    # If no csv files uploaded, error message.
    if LoadData.objects.count() == 0:
        messages.error(request, 'Error: No data to analyse')
        return render(request, 'data_analytics.html')
    else:
        objects = LoadData.objects.all()
        max_frequency = get_max_freq(objects)
        performance_variables_to_select = []
        there_is_event_file = False
        # devices_files_data = []
        new_csv_dict = {}

        for obj in objects:
            csv = pd.read_csv(obj.csv.name, ";", )
            performance_variables_to_select += csv.columns.values.tolist()

        for obj in objects:
            data = {}
            csv = pd.read_csv(obj.csv.name, ";", )
            performance_variables = csv.columns.values.tolist()

            for i in performance_variables:
                data[i] = []

            if obj.event_file == 0:
                for row in csv.values.tolist():
                    for (i, j) in zip(row, performance_variables):
                        data[j].append(i)

                for k, v in dropwhile(lambda x: x[0] != 'TMilisegundos', data.items()):
                    new_csv_dict[k] = v
                process_event_data(new_csv_dict, max_frequency, obj.frequency)
                there_is_event_file = True
            else:
                for row in csv.values.tolist():
                    for (i, j) in zip(row, performance_variables):
                        data[j].append(i)
                    # manera temps menor
                    # devices_files_data.append(data)
                if there_is_event_file:
                    value = new_csv_dict.get("TMilisegundos")[0]
                    process_device_data(data, value, max_frequency, obj.frequency)
                else:
                    process_device_data(data, 0, max_frequency, obj.frequency)

        context = {'perf_vars_list': performance_variables_to_select}
        return render(request, 'data_analytics.html', context)


# Posar el fitxer a la frequencia més gran dels fitxers carregats
def process_event_data(csv_dict, max_frequency, curr_frequency):
    new_csv = pd.DataFrame(csv_dict).to_csv(index=False, sep=";")
    # Only one file with maximum frequency, the others with less frequency
    if curr_frequency < max_frequency:
        interpol(new_csv, curr_frequency, max_frequency)


def interpol(csv, max_freq, curr_freq):
    pass


# Posar el fitxer a la frequencia més gran dels fitxers carregats
def process_device_data(data_to_csv, value_first_time, max_frequency, curr_frequency):
    new_array_starting_0 = []
    new_array_time_starting_value_events = []
    for n in range(0, len(data_to_csv.get("TIME")) + value_first_time):
        new_array_starting_0.append(n)

    if value_first_time != 0:
        for i in dropwhile(lambda x: x != value_first_time, new_array_starting_0):
            new_array_time_starting_value_events.append(i)
        data_to_csv["TIME"] = new_array_time_starting_value_events
    else:
        data_to_csv["TIME"] = new_array_starting_0

    new_csv = pd.DataFrame(data_to_csv).to_csv(index=False, sep=";")
    if curr_frequency < max_frequency:
        interpol(new_csv, max_frequency, curr_frequency)


"""
            for csv in render_data:
                for value in csv.keys():
                    # list with name of performance vars.
                    vars_perf.append(value)
                for value in csv.values():
                    # list of lists, each list with the values of their associated performance var.
                    data_values_vars_perf.append(value)
                    
        context = {'perf_vars_list': performance_variables_to_select, 'column_titles': vars_perf,
                   'values_each_perf_var': data_values_vars_perf, 'values': values}
        return render(request, 'data_analytics.html', context)
"""


def line_chart(request):
    return render(request, 'line_chart.html')
