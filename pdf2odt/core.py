## @namespace pdf2odt.core
## @brief Core functions of the package

from argparse import ArgumentParser, RawTextHelpFormatter
from colorama import Fore, Style, init as colorama_init
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from gettext import translation
from glob import glob
from multiprocessing import cpu_count
from PIL import Image
from pdf2odt.version import __versiondate__, __version__
from pkg_resources import resource_filename
from platform import system as platform_system
from officegenerator import ODT_Standard
from odf.text import P
from os import chdir,  path,  getcwd
from shutil import copyfile, which
from subprocess import check_output, STDOUT
from tempfile import TemporaryDirectory
from tqdm import tqdm
from sys import exit

try:
    t=translation('pdf2odt', resource_filename("pdf2odt","locale"))
    _=t.gettext
except:
    _=str
  
def detect_external_bins(args):
    
    if args.tesseract and which("tesseract") is None:
        print(_("You must install tesseract and add it to the path"))
        exit(4)
    if which("pdftoppm") is None or which("pdfinfo") is None:
        print(_("You must install poppler"))
        exit(4)
  

## Checks if filename is a pdf  
def poppler_check_is_pdf(filename):  
    if poppler_get_pdf_num_pages(filename)==0:
        return False
    return True

def poppler_get_pdf_num_pages(filename):
    if platform_system()=="Windows":
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
    if platform_system()=="Windows":
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
    
def process_pdf_page(args, number, numpages):
    zfill=str(number).zfill(len(str(numpages))) 
    if platform_system()=="Windows":
        pdftoppm_command=f"pdftoppm.exe -r {args.resolution} -f {number} -l {number} -png file.pdf pdfpage"
        tesseract_command=f"tesseract.exe pdfpage-{zfill}.png pdfpage-{zfill} -l {args.tesseract_language}"
    else:
        pdftoppm_command=f"pdftoppm -r {args.resolution} -f {number} -l {number} -png file.pdf pdfpage"
        tesseract_command=f"tesseract pdfpage-{zfill}.png pdfpage-{zfill} -l {args.tesseract_language}"
    #print(pdftoppm_command)
    #print(tesseract_command)
    check_output(pdftoppm_command, shell=True,  stderr=STDOUT)
    if args.tesseract==True:
        check_output(tesseract_command, shell=True,  stderr=STDOUT)
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
    parser.add_argument('--tesseract_language', help=_("Language used in tesseract command. Default is eng"), action="store", default="eng")
    parser.add_argument('--resolution', help=_("Sets DPI image resolution. Default is 300"), action="store", default="300")
    parser.add_argument('--tesseract', help=_("Uses tesseract ocr and insert result after image in ODT document"), action="store_true", default=False)
    parser.add_argument('output', help=_("Output odt file"), action="store")

    args=parser.parse_args(arguments)
    
    detect_external_bins(args)
    
    cwd=getcwd()

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


    with TemporaryDirectory() as tmpdirname:#Exiting this with tmpdirname is deleted. To debug you must do it inside this with
        
        #Copy pdf to temporal dir
        copyfile(args.pdf, f"{tmpdirname}/file.pdf")
        chdir(tmpdirname)
        
        #Launching concurrent process
        futures=[]
        executor = ProcessPoolExecutor(max_workers=cpu_count())
        for number in range(numpages):
            futures.append(executor.submit(process_pdf_page, args, number+1, numpages))
        for f in tqdm(as_completed(futures), total=len(futures)):
            pass

        #Generating ODT
        doc=ODT_Standard("file.odt")
        pdf=path.basename(args.pdf)
        odt=path.basename(args.output)
        doc.setMetadata(_("Converting PDF to ODT"),  _("Converting {} to {} using odt2pdf-{}").format(pdf, odt, __version__), "odt2pdf")
        
        for filename in sorted(glob("pdfpage*.png")):
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
                for line in open(filename[:-4] +".txt", "r", encoding='UTF-8').readlines():
                    p=P(stylename="Standard")
                    p.addText(line)
                    doc.insertInCursor(p, after=True)
        doc.save()
        
        # Copies generated file to output
        chdir(cwd)
        copyfile(f"{tmpdirname}/file.odt", args.output)
   
        #system(f"ls -la {tmpdirname}")
        
    print(Style.BRIGHT + _("ODT generation took {}").format(Fore.GREEN + str(datetime.now()-start)))
