import requests
import os

url = "https://cairesimoveis1.superlogica.net/clients/areadocondomino/publico/arquivos?accesskey=230a42383fb4e24e7682def1803de17054de0ee3&ferramenta=DESPESA&id=62399&idParcela=66840"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, allow_redirects=True)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Primeiros 50 bytes: {response.content[:50]}")

if b"%PDF" in response.content[:10]:
    print("SUCESSO: É um PDF!")
else:
    print("FALHA: Continua sendo HTML ou outro formato.")
