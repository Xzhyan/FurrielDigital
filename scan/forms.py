from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):

        if isinstance(data, (list, tuple)):
            return [super().clean(d, initial) for d in data]

        return super().clean(data, initial)


class ScanForm(forms.Form):
    scan_file = MultipleFileField(
        required=True,
        widget=MultipleFileInput(attrs={
            'accept': ".pdf",
            'multiple': True,
            'class': "h-20 bg-slate-900 rounded-md shadow-md p-2"
        })
    )
    text_scan = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': "Digite um nome para escanear...",
            'class': "bg-slate-900 rounded-md shadow-md p-2"
        })
    )

