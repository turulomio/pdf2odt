"""Test suite for pdf2odt core functionality."""

import pytest
import pymupdf
from pathlib import Path
from PIL import Image as PILImage, ImageDraw
from odfdo import Document
from pdf2odt.core import main, main_command, pdf_check_is_pdf, pdf_get_pdf_num_pages


def test_pdf_with_text(tmp_path):
    """Test converting a multi-page PDF containing pure vector text."""
    pdf_path = tmp_path / "test_text.pdf"
    odt_path = tmp_path / "test_text.odt"

    doc = pymupdf.open()
    page1 = doc.new_page()
    page1.insert_text((50, 72), "First page native text")
    page2 = doc.new_page()
    page2.insert_text((50, 72), "Second page native text")
    doc.save(pdf_path)
    doc.close()

    assert pdf_path.exists()

    main_command(str(pdf_path), 300, True, str(odt_path))

    assert odt_path.exists()

    odt_doc = Document(odt_path)
    frames = odt_doc.body.frames
    assert len(frames) == 2
    for frame in frames:
        assert frame.get_attribute("text:anchor-type") == "as-char"

    paragraphs_text = " ".join([p.text_recursive for p in odt_doc.body.paragraphs])
    assert "First page native text" in paragraphs_text
    assert "Second page native text" in paragraphs_text


def test_pdf_with_images(tmp_path):
    """Test converting a PDF containing a scanned bitmap image via RapidOCR."""
    img_path = tmp_path / "temp_scanned.png"
    pdf_path = tmp_path / "test_scanned.pdf"
    odt_path = tmp_path / "test_scanned.odt"

    # Draw image with clear text to trigger RapidOCR
    img = PILImage.new("RGB", (800, 300), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((50, 100), "TEXTO EN IMAGEN ESCANEADA", fill="black")
    img.save(img_path)

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_image(pymupdf.Rect(50, 50, 450, 200), filename=str(img_path))
    doc.save(pdf_path)
    doc.close()

    assert pdf_path.exists()

    main_command(str(pdf_path), 300, True, str(odt_path))

    assert odt_path.exists()

    odt_doc = Document(odt_path)
    frames = odt_doc.body.frames
    assert len(frames) == 1
    assert frames[0].get_attribute("text:anchor-type") == "as-char"

    # RapidOCR should have recognized text from the image
    paragraphs_text = " ".join([p.text_recursive for p in odt_doc.body.paragraphs])
    assert "TEXTO" in paragraphs_text or "ESCANEADA" in paragraphs_text


def test_pdf_with_text_and_images(tmp_path):
    """Test converting a PDF containing both native text and an embedded image with text."""
    img_path = tmp_path / "temp_mixed.png"
    pdf_path = tmp_path / "test_mixed.pdf"
    odt_path = tmp_path / "test_mixed.odt"

    # Draw image with text
    img = PILImage.new("RGB", (800, 200), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((50, 80), "TEXTO DENTRO DE LA IMAGEN", fill="black")
    img.save(img_path)

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "Texto nativo junto a imagen")
    page.insert_image(pymupdf.Rect(50, 100, 450, 250), filename=str(img_path))
    doc.save(pdf_path)
    doc.close()

    assert pdf_path.exists()

    main_command(str(pdf_path), 300, True, str(odt_path))

    assert odt_path.exists()

    odt_doc = Document(odt_path)
    frames = odt_doc.body.frames
    assert len(frames) == 1
    assert frames[0].get_attribute("text:anchor-type") == "as-char"

    paragraphs_text = " ".join([p.text_recursive for p in odt_doc.body.paragraphs])
    # Verify BOTH native text and OCR text from inside the image are present
    assert "Texto nativo junto a imagen" in paragraphs_text
    assert "TEXTO" in paragraphs_text and ("IMAGEN" in paragraphs_text or "DENTRO" in paragraphs_text)


def test_pdf_without_ocr(tmp_path):
    """Test converting a PDF when OCR extraction is disabled (--ocr flag omitted)."""
    pdf_path = tmp_path / "test_no_ocr.pdf"
    odt_path = tmp_path / "test_no_ocr.odt"

    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Sample text without OCR requested")
    doc.save(pdf_path)
    doc.close()

    main_command(str(pdf_path), 150, False, str(odt_path))

    assert odt_path.exists()
    odt_doc = Document(odt_path)
    assert len(odt_doc.body.frames) == 1
    # Without OCR, no text paragraphs should be added
    paragraphs_text = " ".join([p.text_recursive for p in odt_doc.body.paragraphs])
    assert "Sample text without OCR requested" not in paragraphs_text


def test_invalid_pdf(tmp_path):
    """Test error handling when supplied with non-existent or invalid PDF files."""
    invalid_path = tmp_path / "non_existent_file.pdf"
    out_path = tmp_path / "out.odt"
    assert pdf_get_pdf_num_pages(str(invalid_path)) == 0
    assert pdf_check_is_pdf(str(invalid_path)) is False

    with pytest.raises(SystemExit) as exc_info:
        main_command(str(invalid_path), 300, False, str(out_path))
    assert exc_info.value.code == 1


def test_pdf_with_blank_image_and_native_text(tmp_path):
    """Test page containing a non-text image alongside native text."""
    img_path = tmp_path / "temp_blank.png"
    pdf_path = tmp_path / "test_blank.pdf"
    odt_path = tmp_path / "test_blank.odt"

    img = PILImage.new("RGB", (200, 200), color="blue")
    img.save(img_path)

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "Texto nativo con imagen sin texto")
    page.insert_image(pymupdf.Rect(50, 100, 250, 300), filename=str(img_path))
    doc.save(pdf_path)
    doc.close()

    main_command(str(pdf_path), 300, True, str(odt_path))
    assert odt_path.exists()

    odt_doc = Document(odt_path)
    paragraphs_text = " ".join([p.text_recursive for p in odt_doc.body.paragraphs])
    assert "Texto nativo con imagen sin texto" in paragraphs_text


def test_main_cli(tmp_path):
    """Test CLI invocation using main() entry point with argument list."""
    pdf_path = tmp_path / "test_cli.pdf"
    odt_path = tmp_path / "test_cli.odt"

    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), "CLI Test Document")
    doc.save(pdf_path)
    doc.close()

    main(["--pdf", str(pdf_path), "--resolution", "150", "--ocr", str(odt_path)])
    assert odt_path.exists()
