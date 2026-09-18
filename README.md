# pdf2odt

`pdf2odt` is a tool developed to integrate PDF files into notes taken with LibreOffice Writer.

Sometimes you need to edit the content while keeping the original document layout. It converts PDF pages into images (anchored as characters in A4) and optionally inserts their content as text after going through OCR.

This tool is not intended to be a 1:1 PDF format cloner.

It uses [PyMuPDF](https://pypi.org/project/pymupdf/) (MuPDF) to perform the conversion.

## Links

- **Project main page:** [https://github.com/turulomio/pdf2odt/](https://github.com/turulomio/pdf2odt/)
- **PyPI web page:** [https://pypi.org/project/pdf2odt/](https://pypi.org/project/pdf2odt/)

## Installation and use in Linux

You need **LibreOffice** with its Python UNO bindings, because the `unogenerator` dependency uses it.

Then just type:

```bash
pip install pdf2odt
```

Once installed, you can use it by typing:

```bash
pdf2odt --pdf doc.pdf doc.odt
```

If you want OCR, install the `tesseract` application and run:

```bash
pdf2odt --pdf doc.pdf --tesseract doc.odt
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

If you want OCR, download [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki) and add its installation directory to the Windows environment PATH:

```cmd
pdf2odt --pdf doc.pdf --tesseract doc.odt
```

## Dependencies

- [unogenerator](https://github.com/turulomio/unogenerator/): to generate ODT files.
- [PyMuPDF](https://pypi.org/project/pymupdf/): to convert PDF to images using PyMuPDF.
- [Tesseract OCR](https://github.com/tesseract-ocr/): for OCR support.
