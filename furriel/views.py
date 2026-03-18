from django.shortcuts import render
from django.shortcuts import get_object_or_404

# Models
from .models import Destinations, Militaries, Presences, Ranks

# Forms
from .forms import FilterForm

def index(request):
    form = FilterForm(request.GET or None)
    presences = Presences.objects.all()

    if form.is_valid():
        military = form.cleaned_data.get('military')
        subunit = form.cleaned_data.get('subunit')
        destination = form.cleaned_data.get('destination')
        date = form.cleaned_data.get('date')

        if military:
            presences = presences.filter(military__name__icontains=military)

        if subunit:
            presences = presences.filter(subunit=subunit)

        if destination:
            presences = presences.filter(destination=destination)

        if date:
            presences = presences.filter(date=date)

    context = {
        'form': form,
        'presences': presences,
    }

    return render(request, 'furriel/index.html', context)