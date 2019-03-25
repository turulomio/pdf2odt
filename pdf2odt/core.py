## @namespace pdf2odt.core
## @brief Core functions of the package
import datetime
import platform
import sys

if platform.system()=="Windows":
    print("This script only works on Linux")
    sys.exit(0)

import argparse
import gettext
import locale
import os
import pkg_resources

from colorama import Fore, Style, init as colorama_init
from pdf2odt.version import __versiondate__, __version__

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
    start=datetime.datetime.now()
    parser=argparse.ArgumentParser(prog='pdf2odt', description=_('Converts a pdf to a LibreOffice Writer document with pages as images'), epilog=_("Developed by Mariano Muñoz 2018-{}".format(__versiondate__.year)), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument('--pdf', help=_("File owner will be changed to this parameter. It does nothing if it's not set."), action="store", default=None)
    parser.add_argument('absolute_path', help=_("Directory who is going to be changed permissions and owner recursivily"), action="store")

    args=parser.parse_args(arguments)

    colorama_init(autoreset=True)

    # Sets locale to get integer format localized strings
    try:
        locale.setlocale(locale.LC_ALL, ".".join(locale.getlocale()))
    except:
        pass
