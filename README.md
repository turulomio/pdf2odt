# pdf2odt

`pdf2odt` is a tool developed to integrate PDF files into notes taken with LibreOffice Writer.

Sometimes you need to edit the content while keeping the original document layout. It converts PDF pages into images (anchored as characters in A4) and optionally extracts and inserts their content as text (using native text extraction via PyMuPDF or OCR via RapidOCR for scanned pages).

This tool is not intended to be a 1:1 PDF format cloner.

It uses [PyMuPDF](https://pypi.org/project/pymupdf/) to render pages and extract native text, [RapidOCR](https://pypi.org/project/rapidocr-onnxruntime/) for OCR, and [odfdo](https://pypi.org/project/odfdo/) to generate the ODT document.

## Links

- **Project main page:** [https://github.com/turulomio/pdf2odt/](https://github.com/turulomio/pdf2odt/)
- **PyPI web page:** [https://pypi.org/project/pdf2odt/](https://pypi.org/project/pdf2odt/)

## Installation and use in Linux

Install via `pip`:

```bash
pip install pdf2odt
```

Once installed, you can use it by typing:

```bash
pdf2odt --pdf doc.pdf doc.odt
```

If you want to extract and insert text (using native text extraction or OCR):

```bash
pdf2odt --pdf doc.pdf --ocr doc.odt
```

## Installation and use in Windows

You need Python installed. It works with the latest version. Don't forget to add Python executables to PATH during the installation process.

Then just type:

```cmd
pip install pdf2odt
```

Now you can use it by typing in the Windows shell:

```cmd
pdf2odt --pdf doc.pdf doc.odt
```

With text extraction / OCR:

```cmd
pdf2odt --pdf doc.pdf --ocr doc.odt
```

## Dependencies

- [odfdo](https://pypi.org/project/odfdo/): to generate ODT files.
- [PyMuPDF](https://pypi.org/project/pymupdf/): to convert PDF to images and extract native text.
- [rapidocr-onnxruntime](https://pypi.org/project/rapidocr-onnxruntime/): for OCR text extraction on scanned images.
- [tqdm](https://pypi.org/project/tqdm/): to show progress bars.
- [colorama](https://pypi.org/project/colorama/): to format console colors.

