# pdf2odt

[![Tests](https://github.com/turulomio/pdf2odt/actions/workflows/tests.yml/badge.svg)](https://github.com/turulomio/pdf2odt/actions/workflows/tests.yml)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pdf2odt)](https://pypi.org/project/pdf2odt/)
[![PyPI version](https://img.shields.io/pypi/v/pdf2odt)](https://pypi.org/project/pdf2odt/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**pdf2odt** is a Python command-line utility and library that converts PDF documents into **LibreOffice Writer (.odt)** documents.

> [!CAUTION]
> ### ⚠️ NOT A GENERAL PDF-TO-ODT CONVERTER
> **This tool is NOT a general-purpose PDF to editable ODT converter (it does not clone the original editable document formatting or layout).**
>
> It is designed for a **very specific use case**: it converts a PDF document into an ODT file by generating **images of each page anchored as a character** in an A4 layout, with the option to **include text detected via native extraction or OCR** appended below each page.

---

## Key Features

- **100% Pure Python & Self-Contained:** No need to install external system tools such as Poppler, Tesseract, or LibreOffice. Everything is installed via `pip`.
- **High-Quality Page Rendering:** Uses [PyMuPDF](https://pypi.org/project/pymupdf/) (MuPDF) for fast and pixel-perfect rendering to PNG images with configurable DPI resolution.
- **Smart Hybrid Text Extraction & OCR:**
  - Extracts native vector text directly from digital PDFs with 100% accuracy and near-zero latency.
  - Automatically runs [RapidOCR](https://pypi.org/project/rapidocr-onnxruntime/) (ONNX Runtime) on scanned images or bitmap pages to recognize text.
- **Character-Anchored Images (`as-char`):** Page images are embedded in the ODT document using [odfdo](https://pypi.org/project/odfdo/) with proportional dimensions and anchored as characters, ensuring consistent layout in LibreOffice Writer.
- **Fast & Multi-Threaded:** Uses Python thread pooling to process pages concurrently across all available CPU cores.

---

## Installation

Install `pdf2odt` using `pip`:

```bash
pip install pdf2odt
```

Or using Poetry:

```bash
poetry add pdf2odt
```

---

## Command-Line Usage

### 1. Basic Conversion
Convert a PDF into an ODT document (renders pages at default 300 DPI):

```bash
pdf2odt --pdf document.pdf output.odt
```

### 2. Conversion with Text Extraction / OCR
Extract native text and perform OCR on images, inserting the text below each page image in the ODT document:

```bash
pdf2odt --pdf document.pdf --ocr output.odt
```

### 3. Custom Image Resolution
Set a custom image resolution in DPI (default is 300 DPI; use lower values like 150 DPI for smaller file sizes):

```bash
pdf2odt --pdf document.pdf --resolution 150 output.odt
```

### 4. Full Options Reference

```text
usage: pdf2odt [-h] [--version] --pdf PDF [--resolution RESOLUTION] [--ocr] output

Converts a pdf to a LibreOffice Writer document with pages as images

positional arguments:
  output                Output odt file

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --pdf PDF             PDF file to convert
  --resolution RESOLUTION
                        Sets DPI image resolution. Default is 300
  --ocr                 Extracts text with page.get_text() or OCR and inserts result after image in ODT document
```

---

## Python API Usage

You can also use `pdf2odt` directly in your Python applications:

```python
from pdf2odt.core import main_command

# Convert a PDF to ODT with 300 DPI and OCR enabled
main_command(
    pdf="path/to/document.pdf",
    resolution=300,
    ocr=True,
    output="path/to/output.odt"
)
```

---

## Dependencies

`pdf2odt` relies on the following Python packages:

- [PyMuPDF](https://pypi.org/project/pymupdf/): High-performance PDF rendering and native text extraction.
- [odfdo](https://pypi.org/project/odfdo/): Pure Python OpenDocument (.odt) document generator.
- [rapidocr-onnxruntime](https://pypi.org/project/rapidocr-onnxruntime/): Lightweight ONNX-powered OCR engine.
- [Pillow](https://pypi.org/project/pillow/): Image dimension and format processing.
- [tqdm](https://pypi.org/project/tqdm/): Console progress bar.
- [colorama](https://pypi.org/project/colorama/): Colored terminal output.

---

## Development & Testing

This project uses [Poetry](https://python-poetry.org/) and [Poe the Poet](https://github.com/nat-n/poethepoet) for development tasks.

### Run Tests
```bash
poetry run poe test
```

### Run Coverage Report
```bash
poetry run poe coverage
```

### Update Translations
```bash
poetry run poe translate
```

---

## License

Distributed under the **GPL-3.0 License**.

