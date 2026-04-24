from pypdf import PdfReader
import os

pdf_path = r"c:\manutencao\auditFinance\doc\01__Prestao_de_contas_Janeiro_2026.pdf"
links = []

try:
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                subtype = annot.get_object().get("/Subtype")
                if subtype == "/Link":
                    uri_dict = annot.get_object().get("/A")
                    if uri_dict and "/URI" in uri_dict:
                        links.append(uri_dict["/URI"])

    print(f"Total de links encontrados: {len(links)}")
    for i, link in enumerate(links):
        print(f"{i+1}: {link}")

    # Salva os links em um txt para o próximo passo
    with open("links_janeiro.txt", "w") as f:
        for link in links:
            f.write(link + "\n")

except Exception as e:
    print(f"Erro ao processar o PDF principal: {e}")
