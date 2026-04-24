import pytest
from src.core.data_extractor import DataExtractor

@pytest.fixture
def data_extractor():
    return DataExtractor()

def test_extract_data_generico(data_extractor):
    text = """
    PRESTAÇÃO DE CONTAS
    Data: 10/05/2026
    Referente a: Manutenção do elevador
    Total: 1500,00
    """
    
    result = data_extractor.extract(text, doc_type="generico")
    
    assert result["data"] == "10/05/2026"
    assert result["valor"] == "1.500,00"
    assert result["descricao"] == "Manutenção do elevador"
    assert result["categoria"] == "Manutenção"

def test_extract_data_conta_luz(data_extractor):
    text = """
    CONTA DE ENERGIA ELÉTRICA
    Vencimento: 15/05/2026
    Consumo de Energia Elétrica
    Valor a Pagar R$ 345,50
    """
    
    result = data_extractor.extract(text, doc_type="conta_luz")
    
    assert result["data"] == "15/05/2026"
    assert result["valor"] == "345,50"
    assert result["descricao"] == "Consumo de Energia Elétrica"
    assert result["categoria"] == "Luz"

def test_classify_document(data_extractor):
    text = "Aqui está a sua conta de energia da eletropaulo"
    doc_type = data_extractor.classify(text)
    assert doc_type == "conta_luz"
    
    text_generic = "Recibo genérico de prestação de serviços"
    doc_type_gen = data_extractor.classify(text_generic)
    assert doc_type_gen == "generico"
