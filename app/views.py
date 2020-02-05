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
        new_csv_dict = {}
        devices = []

        for obj in objects:
            csv = pd.read_csv(obj.csv.name, ";", )
            performance_variables_to_select += csv.columns.values.tolist()

        for obj in objects:
            data = {}
            csv = pd.read_csv(obj.csv.name, ";")
            performance_variables = csv.columns.values.tolist()

            for i in performance_variables:
                data[i] = []

            if obj.event_file == 0:
                for row in csv.values.tolist():
                    for (i, j) in zip(row, performance_variables):
                        data[j].append(i)
                for k, v in dropwhile(lambda x: x[0] != 'TMilisegundos', data.items()):
                    new_csv_dict[k] = v
                process_event_data(new_csv_dict, obj.frequency)
                there_is_event_file = True
            else:
                for row in csv.values.tolist():
                    for (i, j) in zip(row, performance_variables):
                        data[j].append(i)
                if there_is_event_file:
                    value = new_csv_dict.get("TMilisegundos")[0]
                    devices.append(process_device_data(data, value, obj.frequency))
                else:
                    devices.append(process_device_data(data, 0, obj.frequency))
        context = {'perf_vars_list': performance_variables_to_select}
        return render(request, 'data_analytics.html', context)


# frecuencia a 1000 Hz. interpolar. Todos los ficheros a 1000 Hz
def process_event_data(csv_dict, curr_frequency):
    time_lasting = csv_dict["DuracionMiliseg"]
    try:
        del csv_dict["DuracionMiliseg"]
    except KeyError:
        print("Key 'DuracionMiliseg' not found")

    max_resample(csv_dict, curr_frequency, time_lasting)


def max_resample(csv_dict, curr_freq, time_lasting):
    df = pd.DataFrame.from_dict(csv_dict, orient="columns")
    df.to_csv("data_interpol.csv")
    csv = pd.read_csv("data_interpol.csv", header=0, index_col=[0])
    performance_variables = csv.columns.values.tolist()
    data = {}
    for i in performance_variables:
        data[i] = []
    if curr_freq == 100:
        interpol_devices(data, csv, performance_variables, 10)
    elif curr_freq == 10:
        interpol_devices(data, csv, performance_variables, 100)
    else:
        interpol_events(data, csv, performance_variables, time_lasting)
    return data


def interpol_events(data, csv, perf_vars, time_lasting):
    for row, time in zip(csv.values.tolist(), time_lasting):
        for (i, j) in zip(row, perf_vars):
            if isinstance(i, int) and j == "TMilisegundos":
                extreme_time_value_to_interpolate = i
                # Interpolate time
                for t in range(extreme_time_value_to_interpolate, time + extreme_time_value_to_interpolate + 1):
                    data[j].append(t)
            else:
                # Interpolate str value
                for z in range(time+1):
                    data[j].append(i)
    # Len de les llistes = 294799. Falta per arribar als 300000. Rellenar el espacio que falta
    # con el ultimo valor de cada lista
    r = 0


def interpol_devices(data, csv, perf_vars, interpol_value):
    extreme_time_value_to_interpolate = 0
    for row in csv.values.tolist():
        for (i, j) in zip(row, perf_vars):
            if isinstance(i, int):
                extreme_time_value_to_interpolate = i
            if extreme_time_value_to_interpolate != 0 and not isinstance(i, int):
                for z in range(interpol_value):
                    # Interpolate value str
                    data[j].append(i)
            if extreme_time_value_to_interpolate != 0 and isinstance(i, int):
                # Interpolate time
                for time in range(extreme_time_value_to_interpolate,
                                  extreme_time_value_to_interpolate + interpol_value):
                    data[j].append(time)


def process_device_data(data_to_csv, value_first_time, curr_frequency):
    new_array_time = []

    if curr_frequency == 100:
        length_new_array = len((data_to_csv.get("TIME")))/curr_frequency*1000+value_first_time
        for n in range(value_first_time, int(round(length_new_array)), 10):
            new_array_time.append(n)
    elif curr_frequency == 10:
        length_new_array = len((data_to_csv.get("TIME")))/curr_frequency*1000+value_first_time
        for t in range(value_first_time, int(round(length_new_array)) + 100, 100):
            new_array_time.append(t)
    data_to_csv["TIME"] = new_array_time

    # Maximum resample = 1000 Hz
    return max_resample(data_to_csv, curr_frequency, None)


def line_chart(request):
    return render(request, 'line_chart.html')
