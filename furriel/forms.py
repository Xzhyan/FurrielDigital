from django import forms
from .models import Destinations, Migrations, Presences, Ranks, Subunits


class FilterForm(forms.Form):
    rank = forms.ModelChoiceField(
        queryset=Ranks.objects.all(),
        required=False,
        empty_label="PG",
        widget=forms.Select(attrs={
            'class': "bg-slate-900 rounded-md shadow-md p-2"
        })
    )

    military = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': "bg-slate-900 rounded-md shadow-md p-2",
            'placeholder': "Nome do militar",
        })
    )

    subunit = forms.ModelChoiceField(
        queryset=Subunits.objects.all(),
        required=False,
        empty_label="Subunidade",
        widget=forms.Select(attrs={
            'class': "bg-slate-900 rounded-md shadow-md p-2"
        })
    )

    destination = forms.ModelChoiceField(
        queryset=Destinations.objects.all(),
        required=False,
        empty_label="Destino",
        widget=forms.Select(attrs={
            'class': "bg-slate-900 rounded-md shadow-md p-2"
        })
    )

    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': "date",
            'class': "bg-slate-900 rounded-md shadow-md p-2"
        })
    )

