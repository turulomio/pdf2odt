"""Core functions and CLI entry point for pdf2odt."""

from argparse import ArgumentParser, RawTextHelpFormatter
from colorama import Fore, Style, init as colorama_init
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from gettext import translation
from importlib.resources import files
from glob import glob
from multiprocessing import cpu_count
from pdf2odt import __versiondate__, __version__
from odfdo import Document, Frame, Paragraph
from PIL import Image as PILImage
from os import chdir, getcwd
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
from tqdm import tqdm
from sys import exit

import pymupdf
from rapidocr_onnxruntime import RapidOCR

try:
    t = translation('pdf2odt', files("pdf2odt") / 'locale')
    _ = t.gettext
except Exception:
    _ = str


def pdf_check_is_pdf(filename):
    """Check if a file exists and is a valid PDF document.

    Args:
        filename (str): Path to the file to check.

    Returns:
        bool: True if the file is a valid PDF with at least 1 page, False otherwise.
    """
    return pdf_get_pdf_num_pages(filename) > 0


def pdf_get_pdf_num_pages(filename):
    """Get the total number of pages in a PDF document.

    Args:
        filename (str): Path to the PDF file.

    Returns:
        int: Number of pages in the PDF document, or 0 if invalid or unreadable.
    """
    try:
        with pymupdf.open(filename) as doc:
            return len(doc)
    except Exception:
        return 0


def process_pdf_page(ocr, resolution, number, numpages):
    """Render a single PDF page to a PNG image and optionally extract its text.

    Args:
        ocr (bool): If True, extract native text or perform OCR.
        resolution (int | str): Image resolution in DPI (e.g. 300).
        number (int): 1-indexed page number to process.
        numpages (int): Total number of pages in the document (used for filename zero-padding).

    Returns:
        int: The processed page number.
    """
    zfill = str(number).zfill(len(str(numpages)))
    png_filename = f"pdfpage-{zfill}.png"
    txt_filename = f"pdfpage-{zfill}.txt"
    with pymupdf.open("file.pdf") as doc:
        page = doc.load_page(number - 1)
        pix = page.get_pixmap(dpi=int(resolution))
        pix.save(png_filename)

        if ocr is True:
            native_text = page.get_text().strip()
            has_images = len(page.get_images()) > 0

            if not has_images and native_text:
                with open(txt_filename, "w", encoding='UTF-8') as f:
                    f.write(native_text)
            else:
                engine = RapidOCR()
                result, _ = engine(png_filename)
                if result:
                    ocr_text = "\n".join([line[1] for line in result])
                    with open(txt_filename, "w", encoding='UTF-8') as f:
                        f.write(ocr_text)
                elif native_text:
                    with open(txt_filename, "w", encoding='UTF-8') as f:
                        f.write(native_text)
    return number


def main(arguments=None):
    """Command-line interface entry point for pdf2odt.

    Args:
        arguments (list[str] | None): Optional list of CLI argument strings.
            If None, arguments are parsed from sys.argv.
    """
    start = datetime.now()
    parser = ArgumentParser(
        prog='pdf2odt',
        description=_('Converts a pdf to a LibreOffice Writer document with pages as images'),
        epilog=_("Developed by Mariano Muñoz 2019-{}").format(__versiondate__.year),
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--pdf', help=_("PDF file to convert"), action="store", default=None, required=True)
    parser.add_argument('--resolution', help=_("Sets DPI image resolution. Default is 300"), action="store", default="300")
    parser.add_argument('--ocr', help=_("Extracts text with page.get_text() or OCR and inserts result after image in ODT document"), action="store_true", default=False)
    parser.add_argument('output', help=_("Output odt file"), action="store")

    args = parser.parse_args(arguments)
    main_command(args.pdf, args.resolution, args.ocr, args.output)
    print(Style.BRIGHT + _("ODT generation took {}").format(Fore.GREEN + str(datetime.now() - start)))


def main_command(pdf, resolution, ocr, output):
    """Convert a PDF document into an ODT Writer document with pages as images.

    Args:
        pdf (str): Path to the input PDF file.
        resolution (int | str): Resolution in DPI for page rendering (default 300).
        ocr (bool): Whether to extract/OCR text and append it after each image.
        output (str): Path for the output ODT file.
    """
    cwd = getcwd()

    colorama_init(autoreset=True)

    # Validate PDF document
    if pdf_check_is_pdf(pdf) is False:
        print(Style.BRIGHT + Fore.RED + _("Filename to convert is not a PDF document"))
        exit(1)

    numpages = pdf_get_pdf_num_pages(pdf)
    print(Style.BRIGHT + _("Detected {} pages in {}").format(Fore.GREEN + str(numpages) + Fore.WHITE, Fore.GREEN + pdf + Fore.WHITE))

    with TemporaryDirectory() as tmpdirname:
        # Copy input PDF to temporary working directory
        copyfile(pdf, f"{tmpdirname}/file.pdf")
        chdir(tmpdirname)

        # Launch concurrent thread pool for page rendering and OCR
        futures = []
        executor = ThreadPoolExecutor(max_workers=cpu_count())
        for number in range(numpages):
            futures.append(executor.submit(process_pdf_page, ocr, resolution, number + 1, numpages))
        for f in tqdm(as_completed(futures), total=len(futures)):
            pass

        # Generate ODT document using odfdo
        doc = Document("text")
        doc.body.clear()
        pdf_name = Path(pdf).name
        odt_name = Path(output).name
        doc.meta.set_title(_("Converting PDF to ODT"))
        doc.meta.set_subject(_("Converting {} to {} using pdf2odt-{}").format(pdf_name, odt_name, __version__))
        doc.meta.set_creator("pdf2odt")

        body = doc.body
        for filename in sorted(glob("pdfpage*.png")):
            with PILImage.open(filename) as img:
                w_px, h_px = img.size
                width_cm = 14.0
                height_cm = round((h_px / w_px) * width_cm, 2)

            image_uri = doc.add_file(str(Path(filename).resolve()))
            frame = Frame.image_frame(
                image=image_uri,
                size=(f"{width_cm}cm", f"{height_cm}cm"),
                anchor_type="as-char",
            )
            p = Paragraph()
            p.append(frame)
            body.append(p)

            txt_filename = filename[:-4] + ".txt"
            if ocr is True and Path(txt_filename).exists():
                with open(txt_filename, "r", encoding="UTF-8") as f:
                    for line in f.readlines():
                        text_line = line.rstrip("\r\n")
                        if text_line:
                            body.append(Paragraph(text_line))

        doc.save("file.odt")

        # Copy generated ODT file to target destination
        chdir(cwd)
        copyfile(f"{tmpdirname}/file.odt", output)
