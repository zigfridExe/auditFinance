"""
Test Routes API
Endpoints para testar individualmente cada componente do sistema
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time

from src.core.ollama_client import OllamaClient
from src.core.gemini_client import GeminiClient
from src.core.llm_wrapper import LLMWrapper
from src.core.ocr_processor import OCRProcessor
from src.core.math_validator import MathValidator
from src.core.database import DatabaseManager

router = APIRouter(prefix="/api/test", tags=["test"])


@router.post("/ollama")
async def test_ollama(request: Dict[str, Any]):
    """Testa comunicação com Ollama"""
    print("[TEST] Iniciando teste Ollama...")
    try:
        model = request.get("model", "qwen2.5:0.5b")
        client = OllamaClient(model=model)

        # Verifica disponibilidade com timeout
        try:
            import asyncio
            # Usa run_in_executor para operação síncrona com timeout
            loop = asyncio.get_event_loop()
            print("[TEST] Verificando disponibilidade do Ollama...")
            available = await asyncio.wait_for(
                loop.run_in_executor(None, client.is_available),
                timeout=5.0
            )
            print(f"[TEST] Ollama disponível: {available}")

            if not available:
                print("[TEST] Ollama não disponível")
                return {
                    "status": "error",
                    "message": "Ollama não está disponível",
                    "available": False
                }

            # Verifica se o modelo existe
            print(f"[TEST] Verificando se modelo {model} existe...")
            model_exists = await asyncio.wait_for(
                loop.run_in_executor(None, client.model_exists),
                timeout=5.0
            )
            print(f"[TEST] Modelo existe: {model_exists}")

            if not model_exists:
                print(f"[TEST] Modelo {model} não encontrado")
                return {
                    "status": "error",
                    "message": f"Modelo {model} não encontrado no Ollama. Execute: ollama pull {model}",
                    "available": True,
                    "model_exists": False
                }

            print("[TEST] Gerando resposta do Ollama...")
            start_time = time.time()
            # Prompt mais curto para teste
            prompt = request.get("prompt", "OK")
            response = await asyncio.wait_for(
                loop.run_in_executor(None, client.generate, prompt),
                timeout=45.0  # Aumentado para 45s
            )
            duration = time.time() - start_time
            print(f"[TEST] Resposta recebida em {duration:.2f}s")

            client.close()

            return {
                "status": "success",
                "available": True,
                "response": response,
                "model": model,
                "duration": f"{duration:.2f}s"
            }
        except asyncio.TimeoutError:
            print("[TEST] TIMEOUT: Ollama não respondeu")
            return {
                "status": "error",
                "message": "Ollama timeout - serviço não respondeu",
                "available": False
            }
    except Exception as e:
        print(f"[TEST] ERRO: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao testar Ollama: {str(e)}",
            "available": False
        }


@router.post("/gemini")
async def test_gemini(request: Dict[str, Any]):
    """Testa comunicação com Gemini API usando variável de ambiente"""
    print("[TEST] Iniciando teste Gemini...")
    try:
        # Não aceita API key do request - usa apenas variável de ambiente
        client = GeminiClient()

        # Verifica disponibilidade
        print("[TEST] Verificando disponibilidade do Gemini...")
        available = client.is_available()
        print(f"[TEST] Gemini disponível: {available}")

        if not available:
            print("[TEST] Gemini não configurado (falta API key)")
            return {
                "status": "error",
                "message": "Gemini API não configurado - adicione GEMINI_API_KEY",
                "available": False
            }

        print("[TEST] Gerando resposta do Gemini...")
        start_time = time.time()
        prompt = request.get("prompt", "OK")
        response = client.generate(prompt)
        duration = time.time() - start_time
        print(f"[TEST] Resposta recebida em {duration:.2f}s")

        client.close()

        return {
            "status": "success",
            "available": True,
            "response": response,
            "duration": f"{duration:.2f}s"
        }
    except Exception as e:
        print(f"[TEST] ERRO: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao testar Gemini: {str(e)}",
            "available": False
        }


@router.post("/detector")
async def test_detector():
    """Testa detector de tipo de PDF"""
    print("[TEST] Iniciando teste Detector...")
    try:
        import asyncio
        detector = PDFTypeDetector()
        print("[TEST] Detector inicializado")

        # Testa com um PDF da pasta archives se existir
        import os
        archives_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "archives")

        test_files = [f for f in os.listdir(archives_dir) if f.endswith('.pdf')] if os.path.exists(archives_dir) else []
        print(f"[TEST] Arquivos PDF encontrados: {len(test_files)}")

        if test_files:
            test_file = os.path.join(archives_dir, test_files[0])
            print(f"[TEST] Testando arquivo: {test_files[0]}")
            loop = asyncio.get_event_loop()
            pdf_type, text = await asyncio.wait_for(
                loop.run_in_executor(None, detector.detect, test_file),
                timeout=10.0
            )
            print(f"[TEST] PDF detectado como: {pdf_type.value}")

            return {
                "status": "success",
                "tested_file": test_files[0],
                "detected_type": pdf_type.value,
                "text_length": len(text),
                "message": f"PDF detectado como: {pdf_type.value}"
            }
        else:
            print("[TEST] Nenhum PDF encontrado")
            return {
                "status": "warning",
                "message": "Nenhum PDF encontrado em archives/ para teste",
                "detector_initialized": True
            }
    except asyncio.TimeoutError:
        print("[TEST] TIMEOUT: Detector demorou muito")
        return {
            "status": "error",
            "message": "Detector timeout - operação demorou muito"
        }
    except Exception as e:
        print(f"[TEST] ERRO: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao testar detector: {str(e)}"
        }


@router.post("/ocr")
async def test_ocr():
    """Testa PaddleOCR"""
    print("[TEST] Iniciando teste OCR...")
    try:
        import asyncio
        print("[TEST] Inicializando OCR...")
        ocr = OCRProcessor()
        print("[TEST] OCR inicializado")

        # Testa com uma imagem se existir
        import os
        archives_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "archives")

        image_files = [f for f in os.listdir(archives_dir) if f.endswith(('.jpg', '.jpeg', '.png'))] if os.path.exists(archives_dir) else []
        print(f"[TEST] Imagens encontradas: {len(image_files)}")

        if image_files:
            test_file = os.path.join(archives_dir, image_files[0])
            print(f"[TEST] Processando imagem: {image_files[0]}")
            loop = asyncio.get_event_loop()
            print(f"[TEST] Chamando executor para OCR...")
            start_time = time.time()
            text = await asyncio.wait_for(
                loop.run_in_executor(None, ocr.extract_text_from_image, test_file),
                timeout=60.0  # Aumentado para 60s
            )
            duration = time.time() - start_time
            print(f"[TEST] OCR concluído em {duration:.2f}s")

            return {
                "status": "success",
                "tested_file": image_files[0],
                "extracted_text_length": len(text),
                "text_preview": text[:200] if text else "Nenhum texto extraído",
                "duration": f"{duration:.2f}s"
            }
        else:
            print("[TEST] Nenhuma imagem encontrada")
            return {
                "status": "warning",
                "message": "Nenhuma imagem encontrada em archives/ para teste",
                "ocr_initialized": True
            }
    except asyncio.TimeoutError:
        print("[TEST] TIMEOUT: OCR demorou muito (30s)")
        return {
            "status": "error",
            "message": "OCR timeout - operação demorou muito (30s)"
        }
    except Exception as e:
        print(f"[TEST] ERRO: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao testar OCR: {str(e)}"
        }


@router.post("/validator")
async def test_validator(request: Dict[str, Any]):
    """Testa validador matemático"""
    print("[TEST] Iniciando teste Validator...")
    try:
        import asyncio
        validator = MathValidator()
        print("[TEST] Validator inicializado")
        documents = request.get("documents", [])

        if not documents:
            print("[TEST] ERRO: Documents array required")
            raise HTTPException(status_code=400, detail="Documents array required")

        print(f"[TEST] Validando {len(documents)} documentos...")
        loop = asyncio.get_event_loop()
        start_time = time.time()
        validation = await asyncio.wait_for(
            loop.run_in_executor(None, validator.validate_batch, documents),
            timeout=10.0
        )
        duration = time.time() - start_time
        print(f"[TEST] Validação concluída em {duration:.2f}s")

        return {
            "status": "success",
            "validation": validation,
            "duration": f"{duration:.2f}s"
        }
    except asyncio.TimeoutError:
        print("[TEST] TIMEOUT: Validator demorou muito")
        return {
            "status": "error",
            "message": "Validator timeout - operação demorou muito"
        }
    except Exception as e:
        print(f"[TEST] ERRO: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao testar validator: {str(e)}"
        }


@router.get("/database")
async def test_database():
    """Testa conexão SQLite"""
    print("[TEST] Iniciando teste Database...")
    try:
        import asyncio
        import tempfile
        temp_db = tempfile.mktemp(suffix='.db')
        print(f"[TEST] Criando DB temporário: {temp_db}")
        db = DatabaseManager(temp_db)  # Usa arquivo temporário
        print("[TEST] Database inicializado")

        loop = asyncio.get_event_loop()
        start_time = time.time()

        # Testa inserção
        print("[TEST] Testando inserção...")
        test_data = {
            "data": "15/01/2026",
            "valor": 1500.50,
            "descricao": "Teste de inserção",
            "categoria": "Teste",
            "extraction_method": "test",
            "extraction_success": True
        }
        doc_id = await asyncio.wait_for(
            loop.run_in_executor(None, db.save_main_document, test_data, "test.pdf"),
            timeout=5.0
        )
        print(f"[TEST] Documento inserido com ID: {doc_id}")

        # Testa leitura
        print("[TEST] Testando leitura...")
        retrieved = await asyncio.wait_for(
            loop.run_in_executor(None, db.get_main_document, doc_id),
            timeout=5.0
        )
        print("[TEST] Leitura concluída")

        # Testa estatísticas
        print("[TEST] Testando estatísticas...")
        stats = await asyncio.wait_for(
            loop.run_in_executor(None, db.get_stats),
            timeout=5.0
        )
        print("[TEST] Estatísticas obtidas")

        duration = time.time() - start_time
        print(f"[TEST] Database test concluído em {duration:.2f}s")

        # Limpa arquivo temporário
        import os
        try:
            os.remove(temp_db)
            print("[TEST] Arquivo temporário removido")
        except:
            pass

        return {
            "status": "success",
            "inserted_id": doc_id,
            "retrieved_data": {
                "id": retrieved["id"],
                "filename": retrieved["filename"],
                "valor": retrieved["valor"]
            },
            "stats": stats,
            "duration": f"{duration:.2f}s"
        }
    except asyncio.TimeoutError:
        print("[TEST] TIMEOUT: Database demorou muito")
        return {
            "status": "error",
            "message": "Database timeout - operação demorou muito"
        }
    except Exception as e:
        print(f"[TEST] ERRO: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao testar database: {str(e)}"
        }


@router.get("/health")
async def health_check():
    """Health check geral do sistema"""
    checks = {}

    # Ollama
    try:
        ollama = OllamaClient()
        checks["ollama"] = ollama.is_available()
    except:
        checks["ollama"] = False

    # Gemini
    try:
        gemini = GeminiClient()
        checks["gemini"] = gemini.is_available()
    except:
        checks["gemini"] = False

    # SQLite
    try:
        import tempfile
        temp_db = tempfile.mktemp(suffix='.db')
        db = DatabaseManager(temp_db)
        checks["database"] = True
        try:
            import os
            os.remove(temp_db)
        except:
            pass
    except:
        checks["database"] = False

    # OCR
    try:
        ocr = OCRProcessor()
        checks["ocr"] = True
    except:
        checks["ocr"] = False

    return {
        "status": "healthy" if all(checks.values()) else "degraded",
        "checks": checks,
        "timestamp": time.time()
    }
