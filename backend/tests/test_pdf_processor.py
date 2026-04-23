import pytest
from unittest.mock import patch, MagicMock
from src.core.pdf_processor import PDFProcessor

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

@patch('src.core.pdf_processor.PdfReader')
def test_extract_text_from_pdf(mock_pdf_reader, pdf_processor):
    # Arrange
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Texto de teste do condomínio"
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_instance

    # Act
    text = pdf_processor.extract_text("dummy.pdf")

    # Assert
    assert text == "Texto de teste do condomínio"
    mock_pdf_reader.assert_called_once_with("dummy.pdf")

@patch('src.core.pdf_processor.PdfReader')
def test_extract_links_from_pdf(mock_pdf_reader, pdf_processor):
    # Arrange
    mock_page = MagicMock()
    # Simula a estrutura de anotações (links) no PyPDF2
    mock_page.get.return_value = [
        MagicMock(get_object=lambda: {
            '/Subtype': '/Link',
            '/A': {'/URI': 'https://s3.amazonaws.com/comprovante1.pdf'}
        })
    ]
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_instance

    # Act
    links = pdf_processor.extract_links("dummy.pdf")

    # Assert
    assert len(links) == 1
    assert links[0] == "https://s3.amazonaws.com/comprovante1.pdf"
