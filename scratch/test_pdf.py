import pdfplumber

path = r"c:\manutencao\auditFinance\backend\teste\janeiro26\missing_176556.pdf"
try:
    with pdfplumber.open(path) as pdf:
        print(f"Sucesso ao abrir! Paginas: {len(pdf.pages)}")
        text = pdf.pages[0].extract_text()
        print(f"Texto extraido (primeiros 50 chars): {text[:50] if text else 'VAZIO'}")
except Exception as e:
    print(f"FALHA CRITICA: {e}")
