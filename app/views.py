from django.shortcuts import render


def home(request):
        return render(request, 'base.html')


def settings(request):
        return render(request, 'settings.html')


def upload(request):
        return render(request, 'upload.html')


def data_analytics(request):
        return render(request, 'data_analytics.html')


def variable_selector(request):
        return render(request, 'variable_selector.html')


def line_chart(request):
        return render(request, 'line_chart.html')
