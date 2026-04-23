import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.core.pdf_processor import PDFProcessor
from src.core.data_extractor import DataExtractor
from src.core.downloader import DocumentDownloader
from src.core.audit import AuditEngine

app = FastAPI(title="Minerador de Contas API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = PDFProcessor()
extractor = DataExtractor()
downloader = DocumentDownloader()
audit_engine = AuditEngine()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Motor de Mineração Ativo"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/mine")
async def mine_pdf(file: UploadFile = File(...)):
    # 1. Salva o arquivo principal temporariamente
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 2. Processa PDF principal
        main_text = processor.extract_text(temp_path)
        main_links = processor.extract_links(temp_path)
        main_data = extractor.extract(main_text)
        
        # 3. Baixa e processa anexos
        attachments_data = []
        for link in main_links:
            att_path = downloader.download(link)
            if att_path:
                att_text = processor.extract_text(att_path)
                att_data = extractor.extract(att_text)
                att_data["source_link"] = link
                attachments_data.append(att_data)
                
        # 4. Auditoria cruzada
        inconsistencies = audit_engine.audit(main_data, attachments_data)
        
        return {
            "main_document": main_data,
            "attachments_found": len(main_links),
            "attachments_processed": len(attachments_data),
            "attachments_data": attachments_data,
            "inconsistencies": inconsistencies
        }
        
    finally:
        # Limpa o temporário, mantendo apenas os arquivados no downloader
        if os.path.exists(temp_path):
            os.remove(temp_path)
