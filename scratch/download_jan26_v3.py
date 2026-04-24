import requests
import os
import re
import time

# Pasta de destino
dest_dir = r"c:\manutencao\auditFinance\backend\teste\janeiro26"
os.makedirs(dest_dir, exist_ok=True)

# Lendo os links de visualização
with open("links_janeiro.txt", "r") as f:
    landing_pages = [line.strip() for line in f.readlines() if line.strip()]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print(f"Iniciando download em 2 etapas (Modo Regex) para {len(landing_pages)} despesas...")

total_baixado = 0

for i, landing_url in enumerate(landing_pages):
    try:
        id_parcela = "desconhecido"
        if "idParcela=" in landing_url:
            id_parcela = landing_url.split("idParcela=")[1].split("&")[0]
        
        print(f"[{i+1}/{len(landing_pages)}] Acessando página da parcela {id_parcela}...")
        
        # Etapa 1: Pega o HTML da landing page
        response = requests.get(landing_url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Erro ao acessar landing page: {landing_url}")
            continue
            
        # Etapa 2: Extrai links de downloadarquivo usando REGEX
        # Padrão: href="...downloadarquivo..."
        html = response.text
        download_links = re.findall(r'href=["\'](https?://[^"\']*downloadarquivo[^"\']*)["\']', html)
        
        # Remove duplicatas mantendo a ordem
        download_links = list(dict.fromkeys(download_links))
        
        if not download_links:
            print(f"Aviso: Nenhum link de download encontrado na página {id_parcela}")
            continue
            
        # Etapa 3: Baixa cada arquivo real
        for j, dl_url in enumerate(download_links):
            filename = f"doc_{id_parcela}_p{j+1}.pdf"
            file_path = os.path.join(dest_dir, filename)
            
            dl_res = requests.get(dl_url, headers=headers, timeout=30)
            if dl_res.status_code == 200:
                if b"%PDF" in dl_res.content[:10]:
                    with open(file_path, "wb") as f:
                        f.write(dl_res.content)
                    print(f"   -> Arquivo {j+1} baixado com sucesso!")
                    total_baixado += 1
                else:
                    print(f"   -> Arquivo {j+1} não é um PDF válido.")
            else:
                print(f"   -> Falha ao baixar arquivo {j+1} (Status {dl_res.status_code})")
        
        time.sleep(0.3)
        
    except Exception as e:
        print(f"Erro na despesa {i+1}: {e}")

print(f"\nDownload concluído! Total de arquivos reais baixados: {total_baixado}")
