from django.shortcuts import render
from collections import defaultdict
import tempfile, os
import fitz, unicodedata

# Forms
from .forms import ScanForm


def normalize_text(text):
    """Função para normalizar o texto antes da pesquisa"""
    return unicodedata.normalize('NFKD', text) \
        .encode("ASCII", "ignore") \
        .decode("ASCII") \
        .lower()


def search_text(temp_path, text):
    """Função que vai buscar o texto dentro do pdf."""

    doc = fitz.open(temp_path)

    role = normalize_text("Cabo de Gds")
    name_parts = normalize_text(text).split()

    try:
        for page_num, page in enumerate(doc):
            content = page.get_text()
            normalize_content = normalize_text(content)

            for role in normalize_content:
                if all(part in normalize_content for part in name_parts):
                    return True, page_num + 1

        return False, None
    
    finally:
        doc.close()


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
                    if found and page == 1: # o 'page = 1' é para minimizar o filtro só até a primeira pagina dos pdfs onde mostra os serviços
                        scanned_files.setdefault(file.name, []).append(page)
                
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