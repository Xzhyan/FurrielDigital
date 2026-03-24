from django.shortcuts import render
from django.http import HttpResponse
from collections import defaultdict
import holidays

# Models
from .models import Destinations, Militaries, Presences, Ranks

# Forms
from .forms import FilterForm

# Gerador de relatorios
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def report_pdf(presences):
    br_holidays = holidays.Brazil() # Holidays obtem os fériados do Brasil.

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename="relatorio.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    elements = []

    styles = getSampleStyleSheet()

    # Titulo do relatorio
    title = Paragraph(
        "Relatório mensal do Furriel Digital",
        styles["Title"]
    )

    # Estilo dos textos da tabela
    table_text_style = ParagraphStyle(
        name="TableText",
        fontName="Helvetica",
        fontSize=9,
        leading=11,  # espaço entre linhas
    )

    elements.append(title)
    elements.append(Spacer(1, 12))

    # Agrupamento da primeira tabela
    grouped_presences = defaultdict(lambda: defaultdict(list))

    # Agrupamento para o resumo calculado dos dias em que o militar esteve fora
    military_stats = defaultdict(
        lambda: {
            'ferias': 0,
            'outros': 0,
            'preta': 0,
            'vermelha': 0
        }
    )

    # Loop principal
    for p in presences:
        date = p.date
        destination = p.destination.destination

        grouped_presences[date][destination].append(p)

        # nome do militar
        name = (f'{p.military.rank.name} {p.military.name}')

        # regras de separação
        is_weekend = date.weekday() >= 5 # fim de semana
        is_holidays = date in br_holidays # feriados

        # Separandos os dias de ferias
        if destination == 'FÉRIAS':
            military_stats[name]['ferias'] += 1

        # Serviço
        elif destination == 'SERVIÇO':
            if is_weekend or is_holidays:
                military_stats[name]['vermelha'] += 1
            
            else:
                military_stats[name]['preta'] += 1

        # Outros dipos de dispensa
        else:
            military_stats[name]['outros'] += 1

    # Cabeçalho do relatorio, primeira tabela
    table_pdf = [
        ["Data", "Destino", "Militares"]
    ]

    # Dados da primeira tabela
    for date, destinations in grouped_presences.items():
        for destination, presences_list in destinations.items():
            militaries = []

            for p in presences_list:
                name = (f'{p.military.rank.name} {p.military.name}')
                militaries.append(name)

            militaries_str = ", ".join(militaries)

            militaries_paragraph = Paragraph(
                militaries_str,
                table_text_style
            )

            table_pdf.append([
                date.strftime("%d/%m/%Y"),
                destination,
                militaries_paragraph
            ])

    # Cria a primeira tabela
    t = Table(
        table_pdf,
        colWidths=[80, 120, 340]
    )

    t.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("VALIGN", (0, 0), (-1, -1), "TOP"),

            ("LEFTPADDING", (0, 0), (-1, -1), 6),

            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    elements.append(t)

    # Espaço entre as tabelas
    elements.append(Spacer(1, 20))

    # Titulo da segunda tabela
    second_title = Paragraph(
        'Resumo calculado dos dias que o militar ficou fora ou de serviço',
        styles['Heading2']
    )
    elements.append(second_title)
    elements.append(Spacer(1, 12))

    # Segunda tabela
    second_table = [
        [
            "Nome",
            "Férias",
            "Outros",
            "SV Preta",
            "SV Vermelha"
        ]
    ]

    for name, stats in military_stats.items():
        name_paragraph = Paragraph(
            name,
            table_text_style
        )

        second_table.append([
            name_paragraph,
            stats['ferias'],
            stats['outros'],
            stats['preta'],
            stats['vermelha']
        ])
    
    second_t = Table(
        second_table,
        colWidths=[200, 70, 70, 90, 110]
    )

    second_t.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("VALIGN", (0, 0), (-1, -1), "TOP"),

            ("LEFTPADDING", (0, 0), (-1, -1), 6),

            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    elements.append(second_t)

    doc.build(elements) # Gera o documento pdf.

    return response


def index(request):
    form = FilterForm(request.GET)
    presences = Presences.objects.none()
    grouped_presences = {}

    if form.is_valid():
        rank = form.cleaned_data.get('rank')
        military = form.cleaned_data.get('military')
        subunit = form.cleaned_data.get('subunit')
        destination = form.cleaned_data.get('destination')
        month = form.cleaned_data.get('month')

        if month:
            presences = Presences.objects.filter(
                date__year=month.year,
                date__month=month.month,
                military__status='ativa'
            ).exclude(
                destination__destination__in=['PRONTO', 'SSV']
            )

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

        presences = presences.select_related(
            'military__rank',
            'military__subunit',
            'destination'
        ).order_by(
            'date', 'destination__destination'
        )

        grouped_presences = defaultdict(lambda: defaultdict(list))

        for p in presences:
            date = p.date
            destination = p.destination.destination
            grouped_presences[date][destination].append(p)

        grouped_presences = {
            date: dict(destinations)
            for date, destinations in grouped_presences.items()
        }


    if request.method == 'POST':
        return report_pdf(presences)

    context = {
        'form': form,
        'presences': presences,
        'gpd_p': grouped_presences,
    }

    return render(request, 'furriel/index.html', context)

