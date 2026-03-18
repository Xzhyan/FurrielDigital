from django.template.loader import get_template
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from xhtml2pdf import pisa

# Models
from .models import Destinations, Militaries, Presences, Ranks

# Forms
from .forms import FilterForm


def save_pdf(presences):
    template = get_template('furriel/index.html')
    html = template.render({'presences': presences})

    return html

def index(request):
    form = FilterForm(request.GET)
    presences = Presences.objects.none()

    if form.is_valid():
        rank = form.cleaned_data.get('rank')
        military = form.cleaned_data.get('military')
        subunit = form.cleaned_data.get('subunit')
        destination = form.cleaned_data.get('destination')
        month = form.cleaned_data.get('month')

        if month:
            presences = Presences.objects.filter(
                date__year=month.year,
                date__month=month.month
            ).select_related(
                'military__rank',
                'military__subunit',
                'destination'
            )

        print(month)

        filters = {}

        if rank:
            filters['military__rank__name__icontains'] = rank

        if military:
            filters['military__name__icontains'] = military

        if subunit:
            filters['military__subunit__name__icontains'] = subunit
        
        if destination:
            filters['destination__destination__icontains'] = destination

        presences = presences.filter(**filters)

    if request.method == 'POST':
        html = save_pdf(presences)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio.pdf"'

        pisa.CreatePDF(html, dest=response)

        return response

    context = {
        'form': form,
        'presences': presences,
    }

    return render(request, 'furriel/index.html', context)

