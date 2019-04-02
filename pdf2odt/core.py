## @namespace pdf2odt.core
## @brief Core functions of the package
import datetime
import platform
import glob
import argparse
import gettext
import os
import pkg_resources

from colorama import Fore, Style, init as colorama_init
from pdf2odt.version import __versiondate__, __version__
from officegenerator import ODT_Standard
from odf.text import P
from PIL import Image
from multiprocessing import cpu_count
from subprocess import check_output, STDOUT
from tqdm import tqdm
from sys import exit

try:
    t=gettext.translation('pdf2odt',pkg_resources.resource_filename("pdf2odt","locale"))
    _=t.gettext
except:
    _=str
  
## Checks if filename is a pdf  
def poppler_check_is_pdf(filename):  
    if poppler_get_pdf_num_pages(filename)==0:
        return False
    return True

def poppler_get_pdf_num_pages(filename):
    if platform.system()=="Windows":
        pdfinfo_command='pdfinfo.exe "{}"'.format( filename) #I add quotes to embrace all command too
    else:
        pdfinfo_command="pdfinfo '{}'".format(filename)

    try:
        output=check_output(pdfinfo_command, shell=True, stderr=STDOUT)
        for line in output.split(b"\n"):
            if line.find(b"Pages:")!=-1:
                return int(line.split(b"Pages:")[1].decode('UTF-8'))
    except:    
        return 0

## Returns a list of tesseract supported languages
## @return list of strings with supported languages
def tesseract_get_supported_languages():
    if platform.system()=="Windows":
        command='tesseract.exe --list-langs'
    else:
        command='tesseract --list-langs'

    result=[]
    try:
        output=check_output(command, shell=True, stderr=STDOUT)
        lines=output.split(b"\n")[1:]
        for line in lines:
            line=line.replace(b"\r", b"")#Needed to parse windows output
            if len(line)>0:
                result.append(line.decode('UTF-8'))
    except:
        pass
    return result
    
def process_page(args, number, numpages):
    zfill=str(number).zfill(len(str(numpages)))
    pngfile="pdf2odt_temporal-{}.png".format(zfill)
    
    if platform.system()=="Windows":
        pdftoppm_command='pdftoppm.exe -r {0} -f {1} -l {1} -png "{2}" pdf2odt_temporal'.format( args.resolution,  number,  args.pdf) #I add quotes to embrace all command too
        tesseract_command='tesseract.exe {0} -l {1} {0}'.format(pngfile, args.tesseract_language)#I add quotes to embrace all command too
    else:
        pdftoppm_command="pdftoppm -png -r {0} -f {1} -l {1} '{2}' pdf2odt_temporal".format( args.resolution, number, args.pdf)
        tesseract_command="tesseract {0} -l {1} {0}".format(pngfile, args.tesseract_language)
    check_output(pdftoppm_command, shell=True,  stderr=STDOUT)
    if args.tesseract==True:
        check_output(tesseract_command, shell=True,  stderr=STDOUT)
    return number

## pdf2odt main script
## If arguments is None, launches with sys.argc parameters. Entry point is pdf2odt:main
## You can call with main(['--pretend']). It's equivalento to os.system('pdf2odt --pretend')
## @param arguments is an array with parser arguments. 
def main(arguments=None):
    start=datetime.datetime.now()
    parser=argparse.ArgumentParser(prog='pdf2odt', description=_('Converts a pdf to a LibreOffice Writer document with pages as images'), epilog=_("Developed by Mariano Muñoz 2019-{}".format(__versiondate__.year)), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--pdf', help=_("PDF file to convert"), action="store", default=None, required=True)
    parser.add_argument('--tesseract_language', help=_("Language used in tesseract command. Default is eng"), action="store", default="eng")
    parser.add_argument('--resolution', help=_("Sets DPI image resolution. Default is 300"), action="store", default="300")
    parser.add_argument('--tesseract', help=_("Uses tesseract ocr and insert result after image in ODT document"), action="store_true", default=False)
    parser.add_argument('output', help=_("Output odt file"), action="store")

    args=parser.parse_args(arguments)

    colorama_init(autoreset=True)
    
    #Make PDF validation
    if poppler_check_is_pdf(args.pdf)==False:
        print(Style.BRIGHT + Fore.RED +_("Filename to convert is not a PDF document"))
        exit(1)
        
    numpages=poppler_get_pdf_num_pages( args.pdf)
    print(Style.BRIGHT +_("Detected {} pages in {}").format(Fore.GREEN + str(numpages) + Fore.WHITE, Fore.GREEN + args.pdf + Fore.WHITE))

    #Checks that tesseract_language is supported
    supported_languages=tesseract_get_supported_languages()
    if args.tesseract==True:
        if args.tesseract_language not in supported_languages:
            print(Style.BRIGHT + Fore.RED +_("Language '{}' is not supported by this tesseract installation. Please use one of this languages {} with --tesseract_language parameter").format(args.tesseract_language, supported_languages))
            exit(1)
        else:
            print(Style.BRIGHT +_("Using '{}' language for Tesseract OCR.").format(Fore.GREEN + args.tesseract_language + Fore.WHITE))

    #Launching concurrent process
    futures=[]
    from concurrent.futures import ProcessPoolExecutor, as_completed
    executor = ProcessPoolExecutor(max_workers=cpu_count()+1)
    for number in range(numpages):
        futures.append(executor.submit(process_page, args, number+1, numpages))
    for f in tqdm(as_completed(futures), total=len(futures)):
        pass

    #Generating ODT
    doc=ODT_Standard(args.output)
    pdf=os.path.basename(args.pdf)
    odt=os.path.basename(args.output)
    doc.setMetadata(_("Converting PDF to ODT"),  _("Converting {} to {} using odt2pdf-{}").format(pdf, odt, __version__), "odt2pdf")
    
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
        if args.tesseract==True:
            for line in open(filename +".txt", "r", encoding='UTF-8').readlines():
                p=P(stylename="Standard")
                p.addText(line)
                doc.insertInCursor(p, after=True)
        
    doc.save()

    #Removing temporal files
    for filename in glob.glob("pdf2odt_temporal*.png"):
        os.remove(filename)
        if args.tesseract==True:
            os.remove(filename+".txt")
        
    print(Style.BRIGHT + _("ODT generation took {}").format(Fore.GREEN + str(datetime.datetime.now()-start)))
