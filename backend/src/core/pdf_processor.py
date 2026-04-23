from pypdf import PdfReader

class PDFProcessor:
    def extract_text(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()

    def extract_links(self, file_path: str) -> list[str]:
        reader = PdfReader(file_path)
        links = []
        for page in reader.pages:
            annotations = page.get('/Annots')
            if annotations:
                for annot in annotations:
                    obj = annot.get_object()
                    if obj.get('/Subtype') == '/Link':
                        action = obj.get('/A')
                        if action and '/URI' in action:
                            links.append(action['/URI'])
        return links
