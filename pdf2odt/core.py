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

try:
    t=gettext.translation('pdf2odt',pkg_resources.resource_filename("pdf2odt","locale"))
    _=t.gettext
except:
    _=str

## pdf2odt main script
## If arguments is None, launches with sys.argc parameters. Entry point is pdf2odt:main
## You can call with main(['--pretend']). It's equivalento to os.system('pdf2odt --pretend')
## @param arguments is an array with parser arguments. For example: ['--max_files_to_store','9']. 
def main(arguments=None):
    if platform.system()=="Windows":
        pdftoppm="pdftoppm.exe"
    else:
        pdftoppm="pdftoppm"
    
    start=datetime.datetime.now()
    parser=argparse.ArgumentParser(prog='pdf2odt', description=_('Converts a pdf to a LibreOffice Writer document with pages as images'), epilog=_("Developed by Mariano Muñoz 2019-{}".format(__versiondate__.year)), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--pdf', help=_("PDF file to convert"), action="store", default=None)
    parser.add_argument('--pdftoppm', help=_("Path to pdftoppm command"), action="store", default=pdftoppm)
    parser.add_argument('output', help=_("Output odt file"), action="store")

    args=parser.parse_args(arguments)

    colorama_init(autoreset=True)

    # Sets locale to get integer format localized strings
    try:
        locale.setlocale(locale.LC_ALL, ".".join(locale.getlocale()))
    except:
        pass

    if platform.system()=="Windows":
        command='""{}" -png "{}" pdf2odt_temporal"'.format(args.pdftoppm, args.pdf) #I add quotes to embrace all command too
    else:
        command="{} -png '{}' pdf2odt_temporal".format(args.pdftoppm, args.pdf)

    os.system(command)

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
    doc.save()

    for filename in glob.glob("pdf2odt_temporal*.png"):
        os.remove(filename)
        
    print(Style.BRIGHT + _("ODT generation took {}").format(Fore.GREEN + str(datetime.datetime.now()-start)))
