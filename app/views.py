from django.shortcuts import render, redirect
# from django.core.files.storage import FileSystemStorage
from .forms import FileForm
from .models import PerformanceData


def home(request):
    return render(request, 'base.html')


def configuration(request):
    return render(request, 'settings.html')

"""
def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
    return render(request, 'upload.html', context)
"""


def file_list(request):
    files = PerformanceData.objects.all()
    return render(request, 'file_list.html', {
        'files': files
    })


def upload_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('file_list')
    else:
        form = FileForm()
    return render(request, 'upload_file.html', {
        'form': form
    })


def data_analytics(request):
    return render(request, 'data_analytics.html')


def variable_selector(request):
    return render(request, 'variable_selector.html')


def line_chart(request):
    return render(request, 'line_chart.html ')
