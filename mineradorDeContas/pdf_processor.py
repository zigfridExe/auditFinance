# mineradorDeContas/pdf_processor.py

import requests
import PyPDF2
import re
import os

def extract_text_from_pdf(pdf_path):
    """
    Extrai texto de um arquivo PDF.
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
    except Exception as e:
        print(f"Erro ao extrair texto do PDF {pdf_path}: {e}")
    return text

def extract_links_from_pdf(pdf_path):
    """
    Extrai URLs de links de um arquivo PDF.
    Foca em links que parecem ser para outros PDFs.
    """
    links = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                if '/Annots' in page:
                    for annot in page['/Annots']:
                        obj = annot.get_object()
                        if '/A' in obj and '/URI' in obj['/A']:
                            uri = obj['/A']['/URI']
                            # Filtra por URLs que provavelmente são PDFs
                            if uri.lower().endswith('.pdf') or 'download' in uri.lower() or 'file' in uri.lower():
                                links.append(uri)
    except Exception as e:
        print(f"Erro ao extrair links do PDF {pdf_path}: {e}")
    return list(set(links)) # Retorna links únicos

def download_pdf(url, output_path):
    """
    Baixa um arquivo PDF de uma URL.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Levanta HTTPError para códigos de status ruins (4xx ou 5xx)
        with open(output_path, 'wb') as pdf_file:
            for chunk in response.iter_content(chunk_size=8192):
                pdf_file.write(chunk)
        print(f"PDF baixado com sucesso: {output_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar PDF de {url}: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado ao baixar PDF de {url}: {e}")
        return False

if __name__ == '__main__':
    # Exemplo de uso (apenas para teste do módulo)
    # Crie um PDF de teste com links para outros PDFs para testar extract_links_from_pdf
    # e um PDF simples para testar extract_text_from_pdf

    # Exemplo de extração de texto
    # Suponha que você tenha um PDF de teste chamado 'test_document.pdf'
    # test_pdf_path = 'path/to/your/test_document.pdf'
    # text = extract_text_from_pdf(test_pdf_path)
    # print("Texto extraído:\n", text[:500]) # Imprime os primeiros 500 caracteres

    # Exemplo de extração de links
    # test_pdf_with_links_path = 'path/to/your/document_with_links.pdf'
    # links = extract_links_from_pdf(test_pdf_with_links_path)
    # print("Links encontrados:", links)

    # Exemplo de download de PDF
    # test_url = 'http://www.africau.edu/images/default/sample.pdf' # Exemplo de PDF público
    # output_dir = 'temp'
    # os.makedirs(output_dir, exist_ok=True)
    # output_file = os.path.join(output_dir, 'sample_downloaded.pdf')
    # if download_pdf(test_url, output_file):
    #     print(f"PDF de exemplo salvo em: {output_file}")
    # else:
    #     print("Falha ao baixar PDF de exemplo.")
