from gettext import translation
from importlib.resources import files
from os import system, chdir
from pdf2odt import __version__

try:
    t=translation('pdf2odt', files("pdf2odt") / 'locale')
    _=t.gettext
except:
    _=str


def doxygen(self):
    print("Creating Doxygen Documentation")
    system("""sed -i -e "41d" doc/Doxyfile""")#Delete line 41
    system("""sed -i -e "41iPROJECT_NUMBER         = {}" doc/Doxyfile""".format(__version__))#Insert line 41
    system("rm -Rf build")
    chdir("doc")
    system("doxygen Doxyfile")
    system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/pdf2odt/ --delete-after")
    chdir("..")

def release():
    print(_("New Release:"))
    print(_("  * Change version and date in version.py"))
    print(_("  * Edit Changelog in README"))
    print("  * python setup.py doc")
    print("  * mcedit locale/es.po")
    print("  * python setup.py doc")
    print("  * python setup.py install")
    print("  * python setup.py doxygen")
    print("  * git commit -a -m 'pdf2odt-{}'".format(__version__))
    print("  * git push")
    print(_("  * Make a new tag in github"))
    print("  * python setup.py sdist upload -r pypi")
    print("  * python setup.py uninstall")
    print(_("  * Create a new gentoo ebuild with the new version"))
    print(_("  * Upload to portage repository")) 

def translate():
    system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o pdf2odt/locale/pdf2odt.pot pdf2odt/*.py")
    system("msgmerge -N --no-wrap -U pdf2odt/locale/es.po pdf2odt/locale/pdf2odt.pot")
    system("msgmerge -N --no-wrap -U pdf2odt/locale/fr.po pdf2odt/locale/pdf2odt.pot")
    system("msgfmt -cv -o pdf2odt/locale/es/LC_MESSAGES/pdf2odt.mo pdf2odt/locale/es.po")
    system("msgfmt -cv -o pdf2odt/locale/fr/LC_MESSAGES/pdf2odt.mo pdf2odt/locale/fr.po")

