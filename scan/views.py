from django.shortcuts import render

# Forms
from .forms import ScanForm

def scan(request):
    form = ScanForm()

    context = {
        'form': form,
    }

    return render(request, 'scan/scan.html', context)