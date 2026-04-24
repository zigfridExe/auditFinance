import os
from pypdf import PdfReader
from PIL import Image, UnidentifiedImageError
# import pytesseract (movido para dentro do bloco de imagem para evitar erros de importação)

class PDFProcessor:
    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        
        # 1. Se for PDF, vai pro leitor com layout espacial (pdfplumber)
        if ext == '.pdf':
            text = ""
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                
                if text.strip():
                    return text.strip()
            except Exception as e:
                # Fallback de segurança para pypdf caso pdfplumber falhe por algum motivo bizarro
                try:
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                    if text.strip():
                        return text.strip()
                except Exception as fallback_err:
                    raise Exception(f"Falha ao ler o PDF: {e} | Fallback: {fallback_err}")
                
        # 2. Se for Imagem, vai pro OCR
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            try:
                import pytesseract
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img, lang='por')
                return text.strip()
            except FileNotFoundError:
                raise Exception("Arquivo de imagem encontrado, mas o Tesseract OCR não está instalado na máquina para extrair o texto.")
            except Exception as e:
                raise Exception(f"Falha ao processar imagem: {e}")
                
        # 3. Se for HTML, extrai o texto com BeautifulSoup
        elif ext in ['.html', '.htm']:
            try:
                from bs4 import BeautifulSoup
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                # Remove scripts e estilos
                for script in soup(["script", "style"]):
                    script.extract()
                text = soup.get_text(separator=' ', strip=True)
                return text
            except Exception as e:
                raise Exception(f"Falha ao extrair texto do HTML: {e}")
                
        # 4. Qualquer outra extensão desconhecida cai na regra do usuário
        else:
            raise Exception(f"Extensão '{ext}' precisa de tratamento específico futuro.")

    def extract_links(self, file_path: str) -> list[str]:
        links = []
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                annotations = page.get('/Annots')
                if annotations:
                    for annot in annotations:
                        obj = annot.get_object()
                        if obj.get('/Subtype') == '/Link':
                            action = obj.get('/A')
                            if action and '/URI' in action:
                                links.append(action['/URI'])
        except Exception:
            # Se for imagem ou pdf quebrado, simplesmente não vai ter links
            pass
        return links
