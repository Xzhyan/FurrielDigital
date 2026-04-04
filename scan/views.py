from django.shortcuts import render
from django.http import HttpResponse
from collections import defaultdict
import tempfile, os, io
import fitz, unicodedata

# Forms
from .forms import ScanForm


def normalize_text(text):
    """Função para normalizar o texto antes da pesquisa"""
    return unicodedata.normalize('NFKD', text) \
        .encode("ASCII", "ignore") \
        .decode("ASCII") \
        .lower()


def create_pdf(results):
    output_doc = fitz.open()

    try:
        for file_path, pages in results.items():
            source_doc = fitz.open(file_path)
            
            for page_num in pages:
                page = source_doc.load_page(page_num)

                new_page = output_doc.new_page(
                    width=page.rect.width,
                    height=page.rect.height
                )

                new_page.show_pdf_page(
                    page.rect,
                    source_doc,
                    page_num
                )

                new_page.insert_text(
                    (72, 20),
                    file_path,
                    fontsize=12
                )
            
            source_doc.close()

        pdf_bytes = output_doc.tobytes()
        return pdf_bytes
    
    finally:
        output_doc.close()


def search_text(temp_path, text):
    """Função que vai buscar o texto dentro do pdf."""

    doc = fitz.open(temp_path)

    name_parts = normalize_text(text).split()

    pages_found = []

    try:
        for page_num, page in enumerate(doc):
            content = page.get_text()
            normalize_content = normalize_text(content)

            if all(part in normalize_content for part in name_parts):
                pages_found.append(page_num)

        return pages_found
    
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

            temp_files = []
            results = {}

            try:
                for file in file_list:
                    # Criando o arquivo temporario para posteriormente escanear
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix='.pdf'
                    ) as temp_file:
                        for chunk in file.chunks():
                            temp_file.write(chunk)

                        temp_path = temp_file.name

                    temp_files.append(temp_path)
                    pages = search_text(temp_path, text)

                    if pages:
                        results[file.name] = {
                            'path': temp_path,
                            'pages': pages
                        }

                if results:
                    final_data = {
                        v['path']: v['pages']
                        for v in results.values()
                    }

                    pdf_bytes = create_pdf(final_data)
                    
                    response = HttpResponse(
                       pdf_bytes,
                       content_type='application/pdf'
                    )
                
                    response['Content-Disposition'] = (
                        'attachment; filename="resultado.pdf"'
                    )
                
                    return response

            finally:
                for path in temp_files:
                    if os.path.exists(path):
                        os.remove(path)

        else:
            print("Form invalido")

    context = { 
        'form': form,
        'scanned_files': dict(scanned_files),
    }

    return render(request, 'scan/scan.html', context)