## @namespace pdf2odt.core
## @brief Core functions of the package

from argparse import ArgumentParser, RawTextHelpFormatter
from colorama import Fore, Style, init as colorama_init
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from gettext import translation
from importlib.resources import files
from glob import glob
from multiprocessing import cpu_count
from pdf2odt import __versiondate__, __version__
from unogenerator import ODT_Standard
from os import chdir, path, getcwd
from shutil import copyfile
from tempfile import TemporaryDirectory
from tqdm import tqdm
from sys import exit

import pymupdf
from rapidocr_onnxruntime import RapidOCR

try:
    t=translation('pdf2odt', files("pdf2odt") / 'locale')
    _=t.gettext
except:
    _=str


## Checks if filename is a pdf  
def pdf_check_is_pdf(filename):  
    return pdf_get_pdf_num_pages(filename) > 0

def pdf_get_pdf_num_pages(filename):
    try:
        with pymupdf.open(filename) as doc:
            return len(doc)
    except:
        return 0


def process_pdf_page(ocr, resolution, number, numpages):
    zfill = str(number).zfill(len(str(numpages))) 
    png_filename = f"pdfpage-{zfill}.png"
    txt_filename = f"pdfpage-{zfill}.txt"
    with pymupdf.open("file.pdf") as doc:
        page = doc.load_page(number - 1)
        pix = page.get_pixmap(dpi=int(resolution))
        pix.save(png_filename)

        if ocr == True:
            native_text = page.get_text().strip()
            if native_text:
                with open(txt_filename, "w", encoding='UTF-8') as f:
                    f.write(native_text)
            else:
                engine = RapidOCR()
                result, _ = engine(png_filename)
                if result:
                    ocr_text = "\n".join([line[1] for line in result])
                    with open(txt_filename, "w", encoding='UTF-8') as f:
                        f.write(ocr_text)
    return number

## pdf2odt main script
## If arguments is None, launches with sys.argc parameters. Entry point is pdf2odt:main
## You can call with main(['--pretend']). It's equivalento to os.system('pdf2odt --pretend')
## @param arguments is an array with parser arguments. 
def main(arguments=None):
    start=datetime.now()
    parser=ArgumentParser(prog='pdf2odt', description=_('Converts a pdf to a LibreOffice Writer document with pages as images'), epilog=_("Developed by Mariano Muñoz 2019-{}".format(__versiondate__.year)), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--pdf', help=_("PDF file to convert"), action="store", default=None, required=True)
    parser.add_argument('--resolution', help=_("Sets DPI image resolution. Default is 300"), action="store", default="300")
    parser.add_argument('--ocr', help=_("Extracts text with page.get_text() or OCR and inserts result after image in ODT document"), action="store_true", default=False)
    parser.add_argument('output', help=_("Output odt file"), action="store")

    args=parser.parse_args(arguments)
    main_command(args.pdf, args.resolution, args.ocr, args.output)
    print(Style.BRIGHT + _("ODT generation took {}").format(Fore.GREEN + str(datetime.now()-start)))


def main_command(pdf, resolution, ocr, output):
    cwd=getcwd()

    colorama_init(autoreset=True)
    
    #Make PDF validation
    if pdf_check_is_pdf(pdf)==False:
        print(Style.BRIGHT + Fore.RED +_("Filename to convert is not a PDF document"))
        exit(1)
        
    numpages=pdf_get_pdf_num_pages(pdf)
    print(Style.BRIGHT +_("Detected {} pages in {}").format(Fore.GREEN + str(numpages) + Fore.WHITE, Fore.GREEN + pdf + Fore.WHITE))

    with TemporaryDirectory() as tmpdirname:#Exiting this with tmpdirname is deleted. To debug you must do it inside this with
        
        #Copy pdf to temporal dir
        copyfile(pdf, f"{tmpdirname}/file.pdf")
        chdir(tmpdirname)
        #Launching concurrent process
        futures=[]
        executor = ProcessPoolExecutor(max_workers=cpu_count())
        for number in range(numpages):
            futures.append(executor.submit(process_pdf_page, ocr, resolution, number+1, numpages))
        for f in tqdm(as_completed(futures), total=len(futures)):
            pass

        #Generating ODT
        with ODT_Standard() as doc:
            pdf=path.basename(pdf)
            odt=path.basename(output)
            doc.setMetadata(_("Converting PDF to ODT"), _("Converting {} to {} using odt2pdf-{}").format(pdf, odt, __version__), "odt2pdf")
            for filename in sorted(glob("pdfpage*.png")):
                doc.addImageParagraph([path.abspath(filename), ], 14, None, style="Illustration", linked=False)
                txt_filename = filename[:-4] + ".txt"
                if ocr==True and path.exists(txt_filename):
                    for line in open(txt_filename, "r", encoding='UTF-8').readlines():
                        doc.addParagraph(line.rstrip("\r\n"))
            doc.save("file.odt")
        
        # Copies generated file to output
        chdir(cwd)
        copyfile(f"{tmpdirname}/file.odt", output)
