import pymupdf
from os import path, remove
from pdf2odt.core import main_command
from odfdo import Document


def test_main():
    # Creates a pdf using pymupdf
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Hello world!")
    doc.save("main.pdf")
    doc.close()

    assert path.exists("main.pdf")

    main_command("main.pdf", 300, True, "main.odt")

    assert path.exists("main.odt")

    odt_doc = Document("main.odt")
    assert len(odt_doc.body.frames) > 0
    assert odt_doc.body.frames[0].get_attribute("text:anchor-type") == "as-char"

    remove("main.pdf")
    remove("main.odt")
