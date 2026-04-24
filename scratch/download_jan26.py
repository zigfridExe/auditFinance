import requests
import os
import time

# Pasta de destino
dest_dir = r"c:\manutencao\auditFinance\backend\teste\janeiro26"
os.makedirs(dest_dir, exist_ok=True)

# Lendo os links extraídos
with open("links_janeiro.txt", "r") as f:
    links = [line.strip() for line in f.readlines() if line.strip()]

print(f"Iniciando download de {len(links)} arquivos...")

for i, url in enumerate(links):
    try:
        # Extrai o idParcela para usar no nome do arquivo
        # Ex: ...&idParcela=66840
        id_parcela = "desconhecido"
        if "idParcela=" in url:
            id_parcela = url.split("idParcela=")[1].split("&")[0]
        
        file_path = os.path.join(dest_dir, f"doc_{id_parcela}_{i+1}.pdf")
        
        if os.path.exists(file_path):
            print(f"[{i+1}/{len(links)}] Já existe: {id_parcela}")
            continue

        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"[{i+1}/{len(links)}] Baixado: {id_parcela}")
        else:
            print(f"[{i+1}/{len(links)}] Falha (Status {response.status_code}): {url}")
        
        # Pequeno delay para não ser bloqueado pelo servidor
        time.sleep(0.5)
        
    except Exception as e:
        print(f"[{i+1}/{len(links)}] Erro: {e}")

print("\nDownload concluído!")
