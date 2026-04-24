import os
import requests
import mimetypes
import re
from urllib.parse import urlparse

class DocumentDownloader:
    def __init__(self, archives_dir: str = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if not archives_dir:
            self.archives_dir = os.path.join(base_dir, "archives")
        else:
            if os.path.isabs(archives_dir) or ":" in archives_dir:
                self.archives_dir = archives_dir
            else:
                clean_dir = archives_dir.lstrip("\\/")
                self.archives_dir = os.path.join(base_dir, clean_dir)
            
        os.makedirs(self.archives_dir, exist_ok=True)

    def download(self, url: str) -> str:
        """Faz o download do arquivo e tenta manter o nome real. Retorna o caminho."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            filename = ""
            # 1. Tenta pegar o nome original vindo do servidor
            if "Content-Disposition" in response.headers:
                cd = response.headers["Content-Disposition"]
                matches = re.findall(r'filename="?([^"]+)"?', cd)
                if matches:
                    filename = matches[0]
            
            # 2. Fallback para a URL
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
            
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            ext = mimetypes.guess_extension(content_type)
            if not ext:
                ext = '.bin'
                
            if not filename or "." not in filename:
                if not filename:
                    filename = f"anexo_{abs(hash(url))}"
                filename = f"{filename}{ext}"
                
            # Limpa caracteres inválidos do Windows
            filename = re.sub(r'[\\/*?:"<>|]', "", filename)
                
            file_path = os.path.join(self.archives_dir, filename)
            
            # Evita sobrescrever arquivos com mesmo nome
            count = 1
            while os.path.exists(file_path):
                name, current_ext = os.path.splitext(filename)
                file_path = os.path.join(self.archives_dir, f"{name}_{count}{current_ext}")
                count += 1
            
            with open(file_path, "wb") as f:
                f.write(response.content)
                
            return file_path
        except Exception as e:
            print(f"Erro ao baixar {url}: {e}")
            return None
