import pdfplumber

path = r"c:\manutencao\auditFinance\backend\teste\janeiro26\missing_176556.pdf"
with pdfplumber.open(path) as pdf:
    text = pdf.pages[0].extract_text()
    print("--- TEXTO BRUTO (REPR) ---")
    print(repr(text))
    print("\n--- TEXTO BRUTO (NORMAL) ---")
    print(text)
