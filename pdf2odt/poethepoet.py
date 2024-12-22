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
    print("""Nueva versión:
  * Cambiar la versión y la fecha en __init__.py
  * Cambiar la versión en pyproject.toml
  * Ejecutar otra vez poe release
  * git checkout -b pdf2odt-{0}
  * pytest
  * Modificar el Changelog en README.md
  * poe coverage con pyvenv
  * poe translate
  * linguist
  * poe translate
  * git commit -a -m 'pdf2odt-{0}'
  * git push
  * Hacer un pull request con los cambios a main
  * Hacer un nuevo tag en GitHub
  * git checkout main
  * git pull
  * poetry build
  * poetry publish --username --password  
""".format(__version__))

def translate():
    system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o pdf2odt/locale/pdf2odt.pot pdf2odt/*.py")
    system("msgmerge -N --no-wrap -U pdf2odt/locale/es.po pdf2odt/locale/pdf2odt.pot")
    system("msgmerge -N --no-wrap -U pdf2odt/locale/fr.po pdf2odt/locale/pdf2odt.pot")
    system("msgfmt -cv -o pdf2odt/locale/es/LC_MESSAGES/pdf2odt.mo pdf2odt/locale/es.po")
    system("msgfmt -cv -o pdf2odt/locale/fr/LC_MESSAGES/pdf2odt.mo pdf2odt/locale/fr.po")


def test():
    system("pytest -W ignore")

def coverage():
    system("coverage run -m pytest && coverage report && coverage html")
