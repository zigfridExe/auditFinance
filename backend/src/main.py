import os
import shutil
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List

from src.core.pdf_processor import PDFProcessor
from src.core.data_extractor import DataExtractor
from src.core.downloader import DocumentDownloader
from src.core.audit import AuditEngine

app = FastAPI(title="Minerador de Contas API", version="0.2.0")

# Lê a porta do frontend do ambiente se disponível
frontend_port = os.getenv("FRONTEND_PORT", "5173")
frontend_url = f"http://localhost:{frontend_port}"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVES_DIR = os.path.join(BASE_DIR, "archives")
os.makedirs(ARCHIVES_DIR, exist_ok=True)
app.mount("/archives", StaticFiles(directory=ARCHIVES_DIR), name="archives")

# Gerenciador de WebSocket para os logs (Janelinha verde)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()
processor = PDFProcessor()
extractor = DataExtractor()
audit_engine = AuditEngine()

@app.websocket("/api/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantém a conexão aberta esperando mensagens do cliente (ping)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/api/mine")
async def mine_pdf(
    file: UploadFile = File(...),
    work_dir: str = Form(None)  # Diretório de trabalho recebido do front
):
    await manager.broadcast(f"> Iniciando processamento do arquivo: {file.filename}")
    
    # Se o usuário informou um diretório, passamos pro downloader
    if work_dir:
        await manager.broadcast(f"> Pasta de trabalho definida: {work_dir}")
        downloader = DocumentDownloader(archives_dir=work_dir)
    else:
        downloader = DocumentDownloader()
        await manager.broadcast(f"> Pasta de trabalho padrão utilizada: {downloader.archives_dir}")

    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        await manager.broadcast("> Lendo PDF principal e extraindo texto...")
        main_text = processor.extract_text(temp_path)
        main_links = processor.extract_links(temp_path)
        await manager.broadcast(f"> Foram encontrados {len(main_links)} links de anexos.")
        
        main_data = extractor.extract(main_text)
        
        attachments_data = []
        links_to_process = list(main_links)
        processed_urls = set()
        
        while links_to_process:
            link = links_to_process.pop(0)
            if link in processed_urls:
                continue
            processed_urls.add(link)
            
            await manager.broadcast(f"> Baixando anexo: {link[:50]}...")
            att_path = downloader.download(link)
            if att_path:
                ext = os.path.splitext(att_path)[1].lower()
                real_filename = os.path.basename(att_path)
                
                # Se for HTML, é uma página de roteamento (ex: Superlógica)
                if ext in ['.html', '.htm']:
                    try:
                        from bs4 import BeautifulSoup
                        with open(att_path, 'r', encoding='utf-8', errors='ignore') as f:
                            soup = BeautifulSoup(f.read(), 'html.parser')
                        new_links = 0
                        for a_tag in soup.find_all('a', href=True):
                            href = a_tag['href']
                            if href.startswith('http') and href not in processed_urls and href not in links_to_process:
                                links_to_process.append(href)
                                new_links += 1
                        if new_links > 0:
                            await manager.broadcast(f"> Página HTML detectada. Encontrados {new_links} novos links de download nela!")
                    except Exception as e:
                        await manager.broadcast(f"> [ERRO] Falha ao analisar HTML em busca de links: {e}")
                    
                    # Tática de Interceptação:
                    # Deletar o arquivo HTML inútil do disco e NÃO colocar no relatório final
                    try:
                        os.remove(att_path)
                    except:
                        pass
                    continue
                
                try:
                    await manager.broadcast(f"> Lendo anexo '{real_filename}'...")
                    att_text = processor.extract_text(att_path)
                    att_data = extractor.extract(att_text)
                    att_data["source_link"] = link
                    att_data["status"] = "sucesso"
                    att_data["nome_arquivo"] = real_filename
                    attachments_data.append(att_data)
                    await manager.broadcast(f"> Sucesso ao processar {real_filename}.")
                except Exception as e:
                    await manager.broadcast(f"> [ERRO] Falha ao ler anexo '{real_filename}': {e}")
                    attachments_data.append({
                        "source_link": link,
                        "status": "erro_leitura",
                        "erro": str(e),
                        "data": None,
                        "valor": None,
                        "descricao": None,
                        "categoria": "Erro",
                        "nome_arquivo": real_filename
                    })
            else:
                await manager.broadcast(f"> [ERRO] Falha no download do anexo.")
                
        await manager.broadcast("> Executando Auditoria Cruzada...")
        inconsistencies = audit_engine.audit(main_data, attachments_data)
        
        await manager.broadcast("> Processo Concluído com sucesso!")
        return {
            "main_document": main_data,
            "attachments_found": len(main_links),
            "attachments_processed": len(attachments_data),
            "attachments_data": attachments_data,
            "inconsistencies": inconsistencies
        }
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/api/mine_folder")
async def mine_local_folder(
    folder_path: str = Form(...)
):
    await manager.broadcast(f"> Iniciando mineração em lote na pasta local: {folder_path}")
    
    if not os.path.exists(folder_path):
        await manager.broadcast(f"> [ERRO] Pasta não encontrada: {folder_path}")
        return {"error": "Pasta não encontrada"}
        
    attachments_data = []
    
    try:
        files = os.listdir(folder_path)
        await manager.broadcast(f"> Encontrados {len(files)} itens na pasta.")
        
        for filename in files:
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[1].lower()
                if ext in ['.pdf', '.jpg', '.jpeg', '.png']:
                    try:
                        await manager.broadcast(f"> Lendo arquivo local '{filename}'...")
                        att_text = processor.extract_text(file_path)
                        att_data = extractor.extract(att_text)
                        att_data["source_link"] = "Pasta Local"
                        att_data["status"] = "sucesso"
                        att_data["nome_arquivo"] = filename
                        attachments_data.append(att_data)
                        await manager.broadcast(f"> Sucesso: {filename}")
                    except Exception as e:
                        await manager.broadcast(f"> [ERRO] Falha ao ler '{filename}': {e}")
                        attachments_data.append({
                            "source_link": "Pasta Local",
                            "status": "erro_leitura",
                            "erro": str(e),
                            "data": None,
                            "valor": None,
                            "descricao": None,
                            "categoria": "Erro",
                            "nome_arquivo": filename
                        })
                        
        # Simulando um doc principal vazio para o relatório e a tabela não quebrarem
        main_data = {"data": None, "valor": None, "descricao": "Mineração de Lote Local", "categoria": "Lote"}
        inconsistencies = audit_engine.audit(main_data, attachments_data)
        
        await manager.broadcast("> Processamento de pasta concluído!")
        return {
            "main_document": main_data,
            "attachments_found": len(attachments_data),
            "attachments_processed": len(attachments_data),
            "attachments_data": attachments_data,
            "inconsistencies": inconsistencies
        }
    except Exception as e:
        await manager.broadcast(f"> [ERRO GRAVE] Falha ao ler a pasta: {str(e)}")
        return {"error": str(e)}

@app.post("/api/mine_batch")
async def mine_batch(
    files: List[UploadFile] = File(...)
):
    await manager.broadcast(f"> Iniciando mineração em lote com {len(files)} arquivos enviados...")
    attachments_data = []
    
    # Garante que a pasta archives existe
    if not os.path.exists("archives"):
        os.makedirs("archives")
    
    for file in files:
        safe_filename = os.path.basename(file.filename.replace("\\", "/"))
        ext = os.path.splitext(safe_filename)[1].lower()
        if ext in ['.pdf', '.jpg', '.jpeg', '.png']:
            save_path = os.path.join("archives", safe_filename)
            try:
                # Salva o arquivo na pasta archives (permanente) para o link funcionar na UI
                with open(save_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                await manager.broadcast(f"> Lendo arquivo '{safe_filename}'...")
                att_text = processor.extract_text(save_path)
                att_data = extractor.extract(att_text)
                att_data["source_link"] = "Lote Local"
                att_data["status"] = "sucesso"
                att_data["nome_arquivo"] = safe_filename
                attachments_data.append(att_data)
                await manager.broadcast(f"> Sucesso: {safe_filename}")
                
            except Exception as e:
                await manager.broadcast(f"> [ERRO] Falha ao ler '{safe_filename}': {e}")
                attachments_data.append({
                    "source_link": "Lote Local",
                    "status": "erro_leitura",
                    "erro": str(e),
                    "data": None,
                    "valor": None,
                    "descricao": None,
                    "categoria": "Erro",
                    "nome_arquivo": safe_filename
                })
                    
    main_data = {"data": None, "valor": None, "descricao": "Lote Processado Manualmente", "categoria": "Lote"}
    inconsistencies = audit_engine.audit(main_data, attachments_data)
    
    await manager.broadcast("> Processamento em lote concluído!")
    return {
        "main_document": main_data,
        "attachments_found": len(attachments_data),
        "attachments_processed": len(attachments_data),
        "attachments_data": attachments_data,
        "inconsistencies": inconsistencies
    }
