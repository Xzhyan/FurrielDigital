from django.shortcuts import render
from collections import defaultdict
import tempfile, os
import fitz

# Forms
from .forms import ScanForm


def search_text(temp_path, text):
    """Função que vai buscar o texto dentro do pdf."""

    doc = fitz.open(temp_path)

    text = text.lower()

    for page_num, page in enumerate(doc):
        content = page.get_text().lower()

        if text in content:
            return True, page_num + 1
    
    return False, None


def scan(request):
    form = ScanForm()

    # Cria o dicionario dos arquivos escaneados e onde o texto se encontra
    scanned_files = defaultdict(list)

    if request.method == 'POST':
        form = ScanForm(request.POST, request.FILES)

        if form.is_valid():
            file_list = request.FILES.getlist('scan_file')
            text = form.cleaned_data['text_scan']

            for file in file_list:
                temp_path = None

                # Criando o arquivo temporario para posteriormente escanear
                try:
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix='.pdf'
                    ) as temp_file:
                        for chunk in file.chunks():
                            temp_file.write(chunk)

                        temp_path = temp_file.name
                    
                    # Faz a busca do texto dentro do arquivo
                    found, page = search_text(temp_path, text)

                    # Se foi encontrado ele adiciona no dicionario
                    if found:
                        scanned_files[file.name].append(page)
                
                finally:
                    if temp_path and os.path.exists(temp_path):
                        os.remove(temp_path)

        else:
            print("Form invalido")

    context = { 
        'form': form,
        'scanned_files': dict(scanned_files),
    }

    return render(request, 'scan/scan.html', context)