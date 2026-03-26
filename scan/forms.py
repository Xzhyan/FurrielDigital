from django import forms

class ScanForm(forms.Form):
    scan_file = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={
            'accept': ".pdf",
            'class': "bg-slate-900 rounded-md shadow-md p-2"
        })
    )
    text_scan = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': "Digite um nome para escanear...",
            'class': "bg-slate-900 rounded-md shadow-md p-2"
        })
    )

