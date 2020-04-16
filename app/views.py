import pandas as pd
import os
import math
import json
import unidecode
import csv as lib_csv

from .forms import *
from django.views.generic import *
from .models import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


def home(request):
    init_time = 0
    fin_time = 0
    frequency = 0
    is_there_configuration = 0
    is_there_key_words_events = 0
    is_there_key_words_devices = 0
    time_ms_name_events = ""
    duration_time_ms_name_events = ""
    time_name_devices = ""
    if ConfigurationSetting.objects.count() == 1:
        is_there_configuration = 1
        frequency = ConfigurationSetting.load().frequency
        init_time = ConfigurationSetting.load().init_time_ms
        fin_time = ConfigurationSetting.load().fin_time_ms
    if KeyWordEventsFile.objects.count() == 1:
        is_there_key_words_events = 1
        time_ms_name_events = KeyWordEventsFile.load().time_ms_name
        duration_time_ms_name_events = KeyWordEventsFile.load().duration_time_ms_name
    if KeyWordDevicesFile.objects.count() == 1:
        is_there_key_words_devices = 1
        time_name_devices = KeyWordDevicesFile.load().time_name

    return render(request, 'base.html', {
        'init_time': init_time, 'fin_time': fin_time, 'frequency': frequency,
        'is_there_configuration': is_there_configuration, 'time_ms_name_events': time_ms_name_events,
        'duration_time_ms_name_events': duration_time_ms_name_events, 'time_name_devices': time_name_devices,
        'is_there_key_words_events': is_there_key_words_events, 'is_there_key_words_devices': is_there_key_words_devices
    })


# "Deleting" user account
def inactive_user(request, username):
    user = User.objects.get(username=username)
    # It is recommended to set this flag to False instead of deleting accounts;
    # that way, if your applications have any foreign keys to users, the foreign keys won't break.
    user.is_active = False
    user.save()
    return redirect('/')


def user_profile(request):
    return render(request, 'registration/user_profile.html')


def exit_session(request):
    is_there_configuration = 0
    if KeyWordEventsFile.objects.count() == 1 or KeyWordDevicesFile.objects.count() == 1 or \
            ConfigurationSetting.objects.count() == 1:
        is_there_configuration = 1
    return render(request, 'exit.html', {
        "is_there_configuration": is_there_configuration
    })


def delete_session(request):
    KeyWordEventsFile.load().delete()
    KeyWordDevicesFile.load().delete()
    ConfigurationSetting.load().delete()

    return redirect('exit')


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


def configuration(request):
    # If no csv files uploaded, error message.
    # If no key words entered, while there are files uploaded of each type, error message.

    objects_data = LoadData.objects.all()

    if LoadData.objects.count() == 0:
        messages.error(request, 'Error: No data to analyse. Please upload some csv files.')
        return render(request, 'settings.html')
    elif KeyWordEventsFile.objects.count() == 0 and is_there_events_file_uploaded(objects_data):
        messages.error(request, 'Error: No events file key words known, although there is events file uploaded.')
        return render(request, 'settings.html')
    elif KeyWordDevicesFile.objects.count() == 0 and is_there_devices_file_uploaded(objects_data):
        messages.error(request, 'Error: No devices file/s key words known, although there is devices file/s uploaded.')
        return render(request, 'settings.html')
    else:
        objects_data = LoadData.objects.all()
        context_init_time = 0
        context_fin_time = 0
        time_ms_name_events_file = ""
        duration_time_ms_name_events_file = ""
        time_name_devices_file = ""
        if KeyWordEventsFile.objects.count() == 1:
            time_ms_name_events_file = KeyWordEventsFile.load().time_ms_name
            duration_time_ms_name_events_file = KeyWordEventsFile.load().duration_time_ms_name
        if KeyWordDevicesFile.objects.count() == 1:
            time_name_devices_file = KeyWordDevicesFile.load().time_name

        for obj in objects_data:
            remove_accent(obj.csv.name)
            csv = pd.read_csv(obj.csv.name, ";")
            performance_variables = csv.columns.values.tolist()
            data = {}

            for i in performance_variables:
                data[i.replace(" ", "_")] = []

            if obj.event_file == 0:
                for row in csv.values.tolist():
                    for (i, j) in zip(row, performance_variables):
                        data[j.replace(" ", "_")].append(i)
                file_dict = process_event_data(data, obj.frequency, time_ms_name_events_file,
                                               duration_time_ms_name_events_file)
                context_init_time, context_fin_time = get_init_time_and_fin_time(file_dict, time_ms_name_events_file)
            else:
                for row in csv.values.tolist():
                    for (i, j) in zip(row, performance_variables):
                        data[j.replace(" ", "_")].append(i)

                if is_there_events_file_uploaded(objects_data):
                    events_csv_dict = get_events_csv_dict(objects_data)
                    value = events_csv_dict.get(time_ms_name_events_file)[0]
                    file_dict = process_device_data(data, value, obj.frequency, time_name_devices_file)
                    context_init_time, context_fin_time = get_init_time_and_fin_time(file_dict, time_name_devices_file)
                else:
                    file_dict = process_device_data(data, 0, obj.frequency, time_name_devices_file)
                    context_init_time, context_fin_time = get_init_time_and_fin_time(file_dict, time_name_devices_file)

    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SettingsForm()

    if context_init_time == 0 and context_fin_time == 0:
        messages.error(request, 'Error in fetching filtering initial time and final time')

    return render(request, 'settings.html', {
        'form': form, 'init_time': context_init_time, 'fin_time': context_fin_time
    })


def get_events_csv_dict(objects_data):
    data = {}

    for obj in objects_data:
        remove_accent(obj.csv.name)
        csv = pd.read_csv(obj.csv.name, ";")
        performance_variables = csv.columns.values.tolist()

        for i in performance_variables:
            data[i.replace(" ", "_")] = []

        if obj.event_file == 0:
            for row in csv.values.tolist():
                for (i, j) in zip(row, performance_variables):
                    data[j.replace(" ", "_")].append(i)

    return data


def get_init_time_and_fin_time(file_dict, time_name):
    init_time = 0
    fin_time = 0

    for key in file_dict.keys():
        if key == time_name:
            init_time = file_dict[key][0]
            fin_time = file_dict[key][-1]

    return init_time, fin_time


def delete_file(request, pk):
    if request.method == 'POST':
        file = LoadData.objects.get(pk=pk)
        file.delete()
    return redirect('file_list')


class FileList(ListView):
    model = LoadData
    template_name = 'uploading/file_list.html'
    context_object_name = 'files'


def set_key_words_events_file(request):
    # If no csv files uploaded, error message.
    if LoadData.objects.count() == 0:
        messages.error(request, 'Error: No data to analyse. Please upload some csv files.')
        return render(request, 'uploading/set_key_words.html')
    else:
        context_perf_vars = set_key_words(0, request)

    if request.method == 'POST':
        form = KeyWordsEventsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('file_list')
    else:
        form = KeyWordsEventsForm()

    return render(request, 'uploading/set_key_words.html', {
        'form': form, 'perf_vars': context_perf_vars
    })


def set_key_words_devices_file(request):
    # If no csv files uploaded, error message.
    if LoadData.objects.count() == 0:
        messages.error(request, 'Error: No data to analyse. Please upload some csv files.')
        return render(request, 'uploading/set_key_words.html')
    else:
        context_perf_vars = set_key_words(1, request)

    if request.method == 'POST':
        form = KeyWordsDevicesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('file_list')
    else:
        form = KeyWordsDevicesForm()
    return render(request, 'uploading/set_key_words.html', {
        'form': form, 'perf_vars': context_perf_vars
    })


def set_key_words(is_events_or_devices_file, request):
    objects_data = LoadData.objects.all()
    context_perf_vars = []

    if is_there_devices_file_uploaded(objects_data) and is_events_or_devices_file == 0 \
            and not is_there_events_file_uploaded(objects_data):
        messages.error(request, 'Error. There are not events files uploaded.')
    elif is_there_events_file_uploaded(objects_data) and is_events_or_devices_file == 1 \
            and not is_there_devices_file_uploaded(objects_data):
        messages.error(request, 'Error. There are not devices files uploaded')
    else:
        for obj in objects_data:
            if obj.event_file == is_events_or_devices_file:
                remove_accent(obj.csv.name)
                csv = pd.read_csv(obj.csv.name, ";")
                performance_variables = csv.columns.values.tolist()
                for i in performance_variables:
                    context_perf_vars.append(i.replace(" ", "_"))

    # Remove duplicate values of the list
    return set(context_perf_vars)


def upload_csv_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        csv_file = request.FILES['csv']
        if form.is_valid() and csv_file.name.endswith('.csv'):
            form.save()
            return redirect('file_list')
        else:
            messages.error(request, 'Error in parameters. Should upload only csv files.')
    else:
        form = FileForm()
    return render(request, 'uploading/upload_file.html', {
        'form': form
    })


def remove_accent(feed):
    csv_f = open(feed, encoding='latin-1', mode='r')
    csv_str = csv_f.read()
    csv_str_removed_accent = unidecode.unidecode(csv_str)
    csv_f.close()
    csv_f = open(feed, 'w')
    csv_f.write(csv_str_removed_accent)


def swap_columns(old_dict, time_name):
    # In the EVENTS file put the time in milliseconds column in the first place of the csv,
    # in order to do the time filter well.
    new_dict = {}

    for key in old_dict.keys():
        if key == time_name:
            new_dict[key] = old_dict[key]
            del old_dict[key]
            break

    for key in old_dict.keys():
        new_dict[key] = old_dict[key]

    return new_dict


def is_there_events_file_uploaded(objects):
    for obj in objects:
        if obj.event_file == 0:
            return True
    return False


def is_there_devices_file_uploaded(objects):
    for obj in objects:
        if obj.event_file == 1:
            return True
    return False


def data_analytics(request):
    # If no csv files uploaded, error message.
    # If no settings configured, error message.
    # If no key words of events file entered, error message.
    # If no key words of devices file/s entered, error message.

    objects_data = LoadData.objects.all()

    if LoadData.objects.count() == 0:
        messages.error(request, 'Error: No data to analyse. Please upload some csv files.')
        return render(request, 'data_analytics.html')
    elif KeyWordEventsFile.objects.count() == 0 and is_there_events_file_uploaded(objects_data):
        messages.error(request, 'Error: No events file key words known, although there is events file uploaded.')
        return render(request, 'data_analytics.html')
    elif KeyWordDevicesFile.objects.count() == 0 and is_there_devices_file_uploaded(objects_data):
        messages.error(request, 'Error: No devices file/s key words known, although there is devices file/s uploaded.')
        return render(request, 'data_analytics.html')
    elif ConfigurationSetting.objects.count() == 0:
        messages.error(request, 'Error: No settings configured. Please go to Settings and enter your configuration.')
        return render(request, 'data_analytics.html')
    else:
        frequency_data_table = ConfigurationSetting.load().frequency
        init_time = ConfigurationSetting.load().init_time_ms
        fin_time = ConfigurationSetting.load().fin_time_ms
        time_ms_name_events_file = ""
        duration_time_ms_name_events_file = ""
        time_name_devices_file = ""
        if KeyWordEventsFile.objects.count() == 1 and is_there_events_file_uploaded(objects_data):
            time_ms_name_events_file = KeyWordEventsFile.load().time_ms_name
            duration_time_ms_name_events_file = KeyWordEventsFile.load().duration_time_ms_name
        if KeyWordDevicesFile.objects.count() == 1 and is_there_devices_file_uploaded(objects_data):
            time_name_devices_file = KeyWordDevicesFile.load().time_name
        dict_devices = []
        dict_down_sampled_files = []

        for obj in objects_data:
            data = {}
            remove_accent(obj.csv.name)
            csv = pd.read_csv(obj.csv.name, ";")
            performance_variables = csv.columns.values.tolist()

            for i in performance_variables:
                data[i.replace(" ", "_")] = []

            if obj.event_file == 0:
                for row in csv.values.tolist():
                    for (element_row, element_perf_var) in zip(row, performance_variables):
                        data[element_perf_var.replace(" ", "_")].append(element_row)
                event_file_dict = process_event_data(data, obj.frequency,
                                                     time_ms_name_events_file, duration_time_ms_name_events_file)
                file_init_time, file_fin_time = get_init_time_and_fin_time(event_file_dict, time_ms_name_events_file)

                if not (fin_time <= file_fin_time and init_time >= file_init_time):
                    messages.error(request, 'Error: It is not possible to analyse data '
                                            'with the settings time parameters. Please re-enter the '
                                            'settings time parameters.')
                    return render(request, 'data_analytics.html')

                dict_down_sampled_files.append(swap_columns(down_sample(event_file_dict, frequency_data_table),
                                                            time_ms_name_events_file))
            else:
                for row in csv.values.tolist():
                    for (element_row, element_perf_var) in zip(row, performance_variables):
                        data[element_perf_var.replace(" ", "_")].append(element_row)
                if is_there_events_file_uploaded(objects_data):
                    events_csv_dict = get_events_csv_dict(objects_data)
                    value = events_csv_dict.get(time_ms_name_events_file)[0]
                    dict_devices.append(process_device_data(data, value, obj.frequency, time_name_devices_file))
                else:
                    dict_devices.append(process_device_data(data, 0, obj.frequency, time_name_devices_file))

        for device_data in dict_devices:
            file_init_time, file_fin_time = get_init_time_and_fin_time(device_data, time_name_devices_file)

            if not (fin_time <= file_fin_time and init_time >= file_init_time):
                messages.error(request, 'Error: It is not possible to analyse data '
                                        'with the settings time parameters. Please re-enter the '
                                        'settings time parameters.')
                return render(request, 'data_analytics.html')

            dict_down_sampled_files.append(down_sample(device_data, frequency_data_table))

        render_data_files = filter_time_files(dict_down_sampled_files,
                                              ConfigurationSetting.load().init_time_ms,
                                              ConfigurationSetting.load().fin_time_ms, time_ms_name_events_file,
                                              duration_time_ms_name_events_file, time_name_devices_file)
        for file in render_data_files:
            for value in file.values():
                for element in value:
                    if isinstance(element, float) and math.isnan(element):
                        value[value.index(element)] = 'null'

        vars_perf = []
        for file in render_data_files:
            for key in file.keys():
                if key not in vars_perf:
                    vars_perf.append(key)

        context = {'perf_vars_list': vars_perf, 'dict_csv_files': json.dumps(render_data_files)}
        return render(request, 'data_analytics.html', context)


def filter_time_files(dict_down_sampled_files, init_filter_time, fin_filter_time, events_time_name,
                      events_duration_time_name, devices_time_name):
    files_to_render = []
    for file in dict_down_sampled_files:
        df = pd.DataFrame.from_dict(file, orient="columns")
        df.to_csv("filtered_time_files.csv")
        csv = pd.read_csv("filtered_time_files.csv", header=0, index_col=[0])
        os.remove("filtered_time_files.csv")
        performance_variables = csv.columns.values.tolist()
        data = {}
        for var in performance_variables:
            data[var] = []
        for row in csv.values.tolist():
            filter_time = False
            for (element_row, element_perf_var) in zip(row, performance_variables):
                if element_perf_var == events_time_name or element_perf_var == devices_time_name:
                    if fin_filter_time >= element_row >= init_filter_time:
                        filter_time = True
                        data[element_perf_var].append(element_row)
                else:
                    if filter_time:
                        data[element_perf_var].append(element_row)
        float_data_to_int_data(data, events_duration_time_name)
        files_to_render.append(data)
    return files_to_render


def float_data_to_int_data(csv_dict, events_duration_time_name):
    keys_floats = {}
    # Handle float numbers except nan
    for key in csv_dict.keys():
        for value in csv_dict[key]:
            if isinstance(value, float):
                if key not in keys_floats.keys() and not math.isnan(value):
                    keys_floats[key] = []
                if key in keys_floats.keys():
                    if math.isnan(value):
                        if key == events_duration_time_name:
                            keys_floats[key].append(0)
                        else:
                            keys_floats[key].append(value)
                    else:
                        keys_floats[key].append(int(math.floor(value)))

    for key in keys_floats:
        csv_dict[key] = keys_floats[key]


# Frequency target 1000 Hz.
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
    # if (time_lasting[-1] + last_time) != limit + first_time:
    time_lasting[-1] = limit + first_time - last_time

    # Maximum re-sample = 1000 Hz
    return max_re_sample(csv_dict, curr_frequency, time_lasting, 0, events_time_name, events_duration_time_name)


# Frequency target 1000 Hz.
def process_device_data(data_to_csv, value_first_time, curr_frequency, time_name):
    new_array_time = []
    length_new_array = 0

    if curr_frequency == 100:
        length_new_array = int(len(data_to_csv.get(time_name))/curr_frequency)*1000+value_first_time
        for time in range(value_first_time, int(round(length_new_array)), 10):
            new_array_time.append(time)
    elif curr_frequency == 10:
        length_new_array = int(len(data_to_csv.get(time_name))/curr_frequency)*1000+value_first_time
        for time in range(value_first_time, int(length_new_array) + 100, 100):
            new_array_time.append(time)
    data_to_csv[time_name] = new_array_time

    # Maximum re-sampling = 1000 Hz
    return max_re_sample(data_to_csv, curr_frequency, None, length_new_array, time_name, None)


def down_sample(dict_csv, table_frequency):
    # Frequency of dict_csv data is 1000 Hz
    if table_frequency != 1000:
        average = int(round(1000/table_frequency))
        for key in dict_csv.keys():
            downsampled = dict_csv.get(key)[0::average]
            # Reduce to ten in the downsample of time.
            # If done, poor bad display of time values
            # Many repeated time values which match different performance vars values.
            """
            if key == events_time_name or key == devices_time_name:
                for element in downsampled:
                    time.append(round(element / 10) * 10)
                dict_csv[key] = time
            else:
                dict_csv[key] = downsampled
                """
            dict_csv[key] = downsampled
    return dict_csv


def max_re_sample(csv_dict, curr_freq, time_lasting, length_array, time_name, events_duration_time_name):
    df = pd.DataFrame.from_dict(csv_dict, orient="columns")
    df.to_csv("data_interpol.csv")
    csv = pd.read_csv("data_interpol.csv", header=0, index_col=[0])
    os.remove("data_interpol.csv")
    performance_variables = csv.columns.values.tolist()
    data = {}
    for var in performance_variables:
        data[var] = []
    if curr_freq == 100:
        interpol_devices(data, csv, performance_variables, 10, length_array)
    elif curr_freq == 10:
        interpol_devices(data, csv, performance_variables, 100, length_array)
    elif curr_freq == 1000:
        for row in csv.values.tolist():
            for (element_row, element_perf_var) in zip(row, performance_variables):
                data[element_perf_var].append(element_row)
    else:
        interpol_events(data, csv, performance_variables, time_lasting, time_name, events_duration_time_name)
    return data


def interpol_events(data, csv, perf_vars, time_lasting, events_time_name, events_duration_time_name):
    for row, time in zip(csv.values.tolist(), time_lasting):
        for (element_row, element_perf_var) in zip(row, perf_vars):
            if isinstance(element_row, int) and element_perf_var == events_time_name:
                extreme_time_value_to_interpolate = element_row
                # Interpolate time
                for new_time in range(extreme_time_value_to_interpolate, time + extreme_time_value_to_interpolate):
                    data[element_perf_var].append(new_time)
            else:
                # Interpolate str value
                for str_value in range(time):
                    data[element_perf_var].append(element_row)
    float_data_to_int_data(data, events_duration_time_name)


def interpol_devices(data, csv, perf_vars, interpol_value, limit_length):
    extreme_time_value_to_interpolate = 0
    for row in csv.values.tolist():
        for (element_row, element_perf_var) in zip(row, perf_vars):
            if isinstance(element_row, int):
                extreme_time_value_to_interpolate = element_row
            if not (extreme_time_value_to_interpolate + interpol_value > limit_length):
                if not isinstance(element_row, int):
                    for str_value in range(interpol_value):
                        # Interpolate value str
                        data[element_perf_var].append(element_row)
                if isinstance(element_row, int):
                    # Interpolate time
                    for time in range(extreme_time_value_to_interpolate,
                                      extreme_time_value_to_interpolate + interpol_value):
                        data[element_perf_var].append(time)


def chart(request):
    objects_data = LoadData.objects.all()
    if LoadData.objects.count() == 0:
        messages.error(request, 'Error: No data to analyse. Please upload some csv events files.')
        return render(request, 'chart.html')
    elif KeyWordEventsFile.objects.count() == 0 and is_there_events_file_uploaded(objects_data):
        messages.error(request, 'Error: No events file key words known, although there is events file uploaded.')
        return render(request, 'chart.html')
    else:
        data = [37, 70, 100, 125, 200, 213, 140, 86]  # get_data()
        # Performance variables as key words for events file.
        labels = ['January', 'February', 'March', 'April', 'dvdv', 'vdvds', 'vvdvvd', '4grehht']
        return render(request, 'chart.html', {
            "data": json.dumps(data), "labels": json.dumps(labels)
        })


# Data of which perf variables as key words for events file
def get_data():
    pass
