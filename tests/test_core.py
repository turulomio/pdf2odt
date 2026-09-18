import pymupdf
from os import path, remove
from PIL import Image as PILImage, ImageDraw
from odfdo import Document
from pdf2odt.core import main_command


def test_pdf_with_text():
    # 1. Creates a multi-page PDF with only native text
    pdf_path = "test_text.pdf"
    odt_path = "test_text.odt"

    doc = pymupdf.open()
    page1 = doc.new_page()
    page1.insert_text((50, 72), "First page native text")
    page2 = doc.new_page()
    page2.insert_text((50, 72), "Second page native text")
    doc.save(pdf_path)
    doc.close()

    assert path.exists(pdf_path)

    main_command(pdf_path, 300, True, odt_path)

    assert path.exists(odt_path)

    odt_doc = Document(odt_path)
    frames = odt_doc.body.frames
    assert len(frames) == 2
    for frame in frames:
        assert frame.get_attribute("text:anchor-type") == "as-char"

    paragraphs_text = " ".join([p.text_recursive for p in odt_doc.body.paragraphs])
    assert "First page native text" in paragraphs_text
    assert "Second page native text" in paragraphs_text

    remove(pdf_path)
    remove(odt_path)


def test_pdf_with_images():
    # 2. Creates a PDF with only a scanned image (bitmap, no native text layer)
    img_path = "temp_scanned.png"
    pdf_path = "test_scanned.pdf"
    odt_path = "test_scanned.odt"

    # Draw image with clear text to trigger RapidOCR
    img = PILImage.new("RGB", (800, 300), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((50, 100), "TEXTO EN IMAGEN ESCANEADA", fill="black")
    img.save(img_path)

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_image(pymupdf.Rect(50, 50, 450, 200), filename=img_path)
    doc.save(pdf_path)
    doc.close()

    assert path.exists(pdf_path)

    main_command(pdf_path, 300, True, odt_path)

    assert path.exists(odt_path)

    odt_doc = Document(odt_path)
    frames = odt_doc.body.frames
    assert len(frames) == 1
    assert frames[0].get_attribute("text:anchor-type") == "as-char"

    # RapidOCR should have recognized text from the image
    paragraphs_text = " ".join([p.text_recursive for p in odt_doc.body.paragraphs])
    assert "TEXTO" in paragraphs_text or "ESCANEADA" in paragraphs_text

    remove(img_path)
    remove(pdf_path)
    remove(odt_path)


def test_pdf_with_text_and_images():
    # 3. Creates a PDF with both an image (containing text) and native vector text
    img_path = "temp_mixed.png"
    pdf_path = "test_mixed.pdf"
    odt_path = "test_mixed.odt"

    # Draw image with text
    img = PILImage.new("RGB", (800, 200), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((50, 80), "TEXTO DENTRO DE LA IMAGEN", fill="black")
    img.save(img_path)

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "Texto nativo junto a imagen")
    page.insert_image(pymupdf.Rect(50, 100, 450, 250), filename=img_path)
    doc.save(pdf_path)
    doc.close()

    assert path.exists(pdf_path)

    main_command(pdf_path, 300, True, odt_path)

    assert path.exists(odt_path)

    odt_doc = Document(odt_path)
    frames = odt_doc.body.frames
    assert len(frames) == 1
    assert frames[0].get_attribute("text:anchor-type") == "as-char"

    paragraphs_text = " ".join([p.text_recursive for p in odt_doc.body.paragraphs])
    # Verify BOTH native text and OCR text from inside the image are present
    assert "Texto nativo junto a imagen" in paragraphs_text
    assert "TEXTO" in paragraphs_text and ("IMAGEN" in paragraphs_text or "DENTRO" in paragraphs_text)

    remove(img_path)
    remove(pdf_path)
    remove(odt_path)
