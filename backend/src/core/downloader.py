import os
import requests
from urllib.parse import urlparse

class DocumentDownloader:
    def __init__(self, archives_dir: str = None):
        if not archives_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.archives_dir = os.path.join(base_dir, "archives")
        else:
            self.archives_dir = archives_dir
            
        os.makedirs(self.archives_dir, exist_ok=True)

    def download(self, url: str) -> str:
        """Faz o download do arquivo e o salva na pasta archives. Retorna o caminho do arquivo."""
        try:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = "documento_anexo.pdf"
                
            file_path = os.path.join(self.archives_dir, filename)
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                f.write(response.content)
                
            return file_path
        except Exception as e:
            print(f"Erro ao baixar {url}: {e}")
            return None
