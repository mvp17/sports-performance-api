import pandas as pd
import os
import math
import json

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
    model = ConfigurationSetting
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


def data_analytics(request):
    # If no csv files uploaded, error message.
    # If no settings configured, error message.
    if LoadData.objects.count() == 0:
        messages.error(request, 'Error: No data to analyse')
        return render(request, 'data_analytics.html')
    elif ConfigurationSetting.objects.count() == 0:
        messages.error(request, 'Error: No settings configured')
        return render(request, 'data_analytics.html')
    else:
        objects_data = LoadData.objects.all()
        frequency_data_table = ConfigurationSetting.load().frequency
        time_ms_name_events_file = ConfigurationSetting.load().time_ms_name
        duration_time_ms_name_events_file = ConfigurationSetting.load().duration_time_ms_name
        there_is_event_file = False
        events_csv_dict = {}
        dict_devices = []
        dict_down_sampled_files = []

        for obj in objects_data:
            data = {}
            csv = pd.read_csv(obj.csv.name, ";")
            performance_variables = csv.columns.values.tolist()

            for i in performance_variables:
                data[i.replace(" ", "_")] = []

            if obj.event_file == 0:
                for row in csv.values.tolist():
                    for (i, j) in zip(row, performance_variables):
                        data[j.replace(" ", "_")].append(i)
                events_csv_dict = data
                event_file_dict = process_event_data(data, obj.frequency,
                                                     time_ms_name_events_file, duration_time_ms_name_events_file)
                dict_down_sampled_files.append(down_sample(event_file_dict, frequency_data_table,
                                                           time_ms_name_events_file))
                there_is_event_file = True
            else:
                for row in csv.values.tolist():
                    for (i, j) in zip(row, performance_variables):
                        data[j.replace(" ", "_")].append(i)
                if there_is_event_file:
                    value = events_csv_dict.get(time_ms_name_events_file)[0]
                    dict_devices.append(process_device_data(data, value, obj.frequency))
                else:
                    dict_devices.append(process_device_data(data, 0, obj.frequency))

        for i in dict_devices:
            dict_down_sampled_files.append(down_sample(i, frequency_data_table, time_ms_name_events_file))

        render_data_files = filter_time_files(dict_down_sampled_files,
                                              ConfigurationSetting.load().init_time_ms,
                                              ConfigurationSetting.load().fin_time_ms, time_ms_name_events_file,
                                              duration_time_ms_name_events_file)
        for file in render_data_files:
            for value in file.values():
                for i in value:
                    if isinstance(i, float) and math.isnan(i):
                        value[value.index(i)] = 'null'

        vars_perf = []
        for file in render_data_files:
            for key in file.keys():
                if key not in vars_perf:
                    vars_perf.append(key)

        context = {'perf_vars_list': vars_perf, 'dict_csv_files': json.dumps(render_data_files)}
        return render(request, 'data_analytics.html', context)


def filter_time_files(dict_down_sampled_files, init_filter_time, fin_filter_time, events_time_name,
                      events_duration_time_name):
    files_to_render = []
    for file in dict_down_sampled_files:
        df = pd.DataFrame.from_dict(file, orient="columns")
        df.to_csv("filtered_time_files.csv")
        csv = pd.read_csv("filtered_time_files.csv", header=0, index_col=[0])
        os.remove("filtered_time_files.csv")
        performance_variables = csv.columns.values.tolist()
        data = {}
        for i in performance_variables:
            data[i] = []
        for row in csv.values.tolist():
            filter_time = False
            for (i, j) in zip(row, performance_variables):
                if j == events_time_name or j == "TIME":
                    if fin_filter_time >= i >= init_filter_time:
                        filter_time = True
                        data[j].append(i)
                else:
                    if filter_time:
                        data[j].append(i)
        float_data_to_int_data(data, events_duration_time_name)
        files_to_render.append(data)
    return files_to_render


def float_data_to_int_data(csv_dict, events_duration_time_name):
    keys_floats = {}
    """Handle float numbers except nan"""
    for key in csv_dict.keys():
        for i in csv_dict[key]:
            if isinstance(i, float):
                if key not in keys_floats.keys() and not math.isnan(i):
                    keys_floats[key] = []
                if key in keys_floats.keys():
                    if math.isnan(i):
                        if key == events_duration_time_name:
                            keys_floats[key].append(0)
                        else:
                            keys_floats[key].append(i)
                    else:
                        keys_floats[key].append(int(math.floor(i)))

    for key in keys_floats:
        csv_dict[key] = keys_floats[key]
    """Handle float numbers except nan"""


# Frequency 1000 Hz.
def process_event_data(csv_dict, curr_frequency, events_time_name, events_duration_time_name):
    float_data_to_int_data(csv_dict, events_duration_time_name)
    time_lasting = csv_dict[events_duration_time_name]
    time = csv_dict[events_time_name]
    first_time = time[0]
    last_time = time[-1]

    # Hesitation here
    limit = int(round(last_time/1000))*1000
    if limit < last_time:
        limit = last_time
    if (time_lasting[-1] + last_time) != limit + first_time:
        time_lasting[-1] = limit + first_time - last_time

    # Maximum re-sample = 1000 Hz
    return max_re_sample(csv_dict, curr_frequency, time_lasting, 0, events_time_name, events_duration_time_name)


# Frequency 1000 Hz.
def process_device_data(data_to_csv, value_first_time, curr_frequency):
    new_array_time = []
    length_new_array = 0

    if curr_frequency == 100:
        length_new_array = int(len(data_to_csv.get("TIME"))/curr_frequency)*1000+value_first_time
        for n in range(value_first_time, int(round(length_new_array)), 10):
            new_array_time.append(n)
    elif curr_frequency == 10:
        length_new_array = int(len(data_to_csv.get("TIME"))/curr_frequency)*1000+value_first_time
        for t in range(value_first_time, int(length_new_array) + 100, 100):
            new_array_time.append(t)
    data_to_csv["TIME"] = new_array_time

    # Maximum re-sampling = 1000 Hz
    return max_re_sample(data_to_csv, curr_frequency, None, length_new_array, None, None)


def down_sample(dict_csv, table_frequency, events_time_name):
    # Frequency of dict_csv data is 1000 Hz
    if table_frequency != 1000:
        average = int(round(1000/table_frequency))
        time = []
        for key in dict_csv.keys():
            downsampled = dict_csv.get(key)[0::average]
            if key == events_time_name or key == "TIME":
                for i in downsampled:
                    time.append(round(i/10)*10)
                dict_csv[key] = time
            else:
                dict_csv[key] = downsampled
    return dict_csv


def max_re_sample(csv_dict, curr_freq, time_lasting, length_array, events_time_name, events_duration_time_name):
    df = pd.DataFrame.from_dict(csv_dict, orient="columns")
    df.to_csv("data_interpol.csv")
    csv = pd.read_csv("data_interpol.csv", header=0, index_col=[0])
    os.remove("data_interpol.csv")
    performance_variables = csv.columns.values.tolist()
    data = {}
    for i in performance_variables:
        data[i] = []
    if curr_freq == 100:
        interpol_devices(data, csv, performance_variables, 10, length_array)
    elif curr_freq == 10:
        interpol_devices(data, csv, performance_variables, 100, length_array)
    elif curr_freq == 1000:
        for row in csv.values.tolist():
            for (i, j) in zip(row, performance_variables):
                data[j].append(i)
    else:
        interpol_events(data, csv, performance_variables, time_lasting, events_time_name, events_duration_time_name)
    return data


def interpol_events(data, csv, perf_vars, time_lasting, events_time_name, events_duration_time_name):
    for row, time in zip(csv.values.tolist(), time_lasting):
        for (i, j) in zip(row, perf_vars):
            if isinstance(i, int) and j == events_time_name:
                extreme_time_value_to_interpolate = i
                # Interpolate time
                for t in range(extreme_time_value_to_interpolate, time + extreme_time_value_to_interpolate):
                    data[j].append(t)
            else:
                # Interpolate str value
                for z in range(time):
                    data[j].append(i)
    float_data_to_int_data(data, events_duration_time_name)
    r = 0


def interpol_devices(data, csv, perf_vars, interpol_value, limit_length):
    extreme_time_value_to_interpolate = 0
    for row in csv.values.tolist():
        for (i, j) in zip(row, perf_vars):
            if isinstance(i, int):
                extreme_time_value_to_interpolate = i
            if not (extreme_time_value_to_interpolate + interpol_value > limit_length):
                if not isinstance(i, int):
                    for z in range(interpol_value):
                        # Interpolate value str
                        data[j].append(i)
                if isinstance(i, int):
                    # Interpolate time
                    for time in range(extreme_time_value_to_interpolate,
                                      extreme_time_value_to_interpolate + interpol_value):
                        data[j].append(time)
