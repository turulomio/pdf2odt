## @namespace pdf2odt.core
## @brief Core functions of the package
import datetime
import platform
import glob
import argparse
import gettext
import locale
import os
import pkg_resources

from colorama import Fore, Style, init as colorama_init
from pdf2odt.version import __versiondate__, __version__
from officegenerator import ODT_Standard
from odf.text import P
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from subprocess import check_output


try:
    t=gettext.translation('pdf2odt',pkg_resources.resource_filename("pdf2odt","locale"))
    _=t.gettext
except:
    _=str


def get_pdf_num_pages(filename):
    if platform.system()=="Windows":
        pdfinfo_command='""pdfinfo.exe" "{}""'.format( filename) #I add quotes to embrace all command too
    else:
        pdfinfo_command="pdfinfo '{}'".format(filename)

    print("Converting pdf to images")
    try:
        output=check_output(pdfinfo_command, shell=True)
        print(output)
    except:
        pass
    



## pdf2odt main script
## If arguments is None, launches with sys.argc parameters. Entry point is pdf2odt:main
## You can call with main(['--pretend']). It's equivalento to os.system('pdf2odt --pretend')
## @param arguments is an array with parser arguments. For example: ['--max_files_to_store','9']. 
def main(arguments=None):
    start=datetime.datetime.now()
    parser=argparse.ArgumentParser(prog='pdf2odt', description=_('Converts a pdf to a LibreOffice Writer document with pages as images'), epilog=_("Developed by Mariano Muñoz 2019-{}".format(__versiondate__.year)), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--pdf', help=_("PDF file to convert"), action="store", default=None)
    parser.add_argument('--tesseract_language', help=_("Language used in t1esseract command. Default is spa"), action="store", default="spa")
    parser.add_argument('--resolution', help=_("Sets DPI image resolution. Default is 300"), action="store", default="300")
    parser.add_argument('--tesseract', help=_("Uses tesseract ocr and insert result after image in ODT document"), action="store_true", default=False)
    parser.add_argument('--output', help=_("Output odt file"), action="store")

    args=parser.parse_args(arguments)

    colorama_init(autoreset=True)

    # Sets locale to get integer format localized strings
    try:
        locale.setlocale(locale.LC_ALL, ".".join(locale.getlocale()))
    except:
        pass

    if platform.system()=="Windows":
        pdftoppm_command='""pdftoppm.exe" -r {} -png "{}" pdf2odt_temporal"'.format( args.resolution,  args.pdf) #I add quotes to embrace all command too
    else:
        pdftoppm_command="pdftoppm -png -r {} '{}' pdf2odt_temporal".format( args.resolution, args.pdf)

    print("Converting pdf to images")
    os.system(pdftoppm_command)

    doc=ODT_Standard(args.output)
    pdf=os.path.basename(args.pdf)
    odt=os.path.basename(args.output)
    doc.setMetadata(_("Converting PDF to ODT"),  _("Converting {} to {} using odt2pdf-{}").format(pdf, odt, __version__), "odt2pdf")
    
    
    get_pdf_num_pages( args.pdf)
    
    
    futures=[]
    with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
        for filename in sorted(glob.glob("pdf2odt_temporal*.png")):
            if platform.system()=="Windows":
                tesseract_command='""tesseract.exe" {1} -l {2} {1}"'.format(filename, args.tesseract_language)#I add quotes to embrace all command too
            else:
                tesseract_command="tesseract {1} -l {2} {1}".format(filename, args.tesseract_language)
            futures.append(executor.submit(os.system, tesseract_command))    

    for filename in sorted(glob.glob("pdf2odt_temporal*.png")):
        img = Image.open(filename)
        x,y=img.size
        cmx=17
        cmy=y*cmx/x
        img.close()
        doc.addImage(filename, filename)
        p = P(stylename="Illustration")
        p.addElement(doc.image(filename, cmx,cmy))
        doc.insertInCursor(p, after=True)
        
        for line in open(filename +".txt", "r").readlines():
            p=P(stylename="Standard")
            p.addText(line)
            doc.insertInCursor(p, after=True)
        
    doc.save()

    for filename in glob.glob("pdf2odt_temporal*.png"):
        os.remove(filename)
        os.remove(filename+".txt")
        
    print(Style.BRIGHT + _("ODT generation took {}").format(Fore.GREEN + str(datetime.datetime.now()-start)))
