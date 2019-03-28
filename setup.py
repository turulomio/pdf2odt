from setuptools import setup, Command
import datetime
import gettext
import os
import platform
import site

gettext.install('pdf2odt', 'pdf2odt/locale')

class Doxygen(Command):
    description = "Create/update doxygen documentation in doc/html"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Creating Doxygen Documentation")
        os.system("""sed -i -e "41d" doc/Doxyfile""")#Delete line 41
        os.system("""sed -i -e "41iPROJECT_NUMBER         = {}" doc/Doxyfile""".format(__version__))#Insert line 41
        os.system("rm -Rf build")
        os.chdir("doc")
        os.system("doxygen Doxyfile")
        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/pdf2odt/ --delete-after")
        os.chdir("..")

class Procedure(Command):
    description = "Create/update doxygen documentation in doc/html"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
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

class Uninstall(Command):
    description = "Uninstall installed files with install"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if platform.system()=="Linux":
            os.system("rm -Rf {}/pdf2odt*".format(site.getsitepackages()[0]))
            os.system("rm /usr/bin/pdf2odt")
        else:
            os.system("pip uninstall pdf2odt")

class Doc(Command):
    description = "Update man pages and translations"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        #es
        os.system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o locale/pdf2odt.pot *.py pdf2odt/*.py")
        os.system("msgmerge -N --no-wrap -U locale/es.po locale/pdf2odt.pot")
        os.system("msgmerge -N --no-wrap -U locale/fr.po locale/pdf2odt.pot")
        os.system("msgfmt -cv -o pdf2odt/locale/es/LC_MESSAGES/pdf2odt.mo locale/es.po")
        os.system("msgfmt -cv -o pdf2odt/locale/fr/LC_MESSAGES/pdf2odt.mo locale/fr.po")


## Version of modele captured from version to avoid problems with package dependencies
__version__= None
with open('pdf2odt/version.py', encoding='utf-8') as f:
    for line in f.readlines():
        if line.find("__version__ =")!=-1:
            __version__=line.split("'")[1]


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(name='pdf2odt',
    version=__version__,
    description='Change files and directories permisions and owner recursivily from current directory',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: System Administrators',
                 'Topic :: System :: Systems Administration',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Programming Language :: Python :: 3',
                ],
    keywords='change permissions ownner files directories',
    url='https://github.com/Turulomio/pdf2odt',
    author='Turulomio',
    author_email='turulomio@yahoo.es',
    license='GPL-3',
    packages=['pdf2odt'],
    entry_points = {'console_scripts': ['pdf2odt=pdf2odt.core:main',
                                       ],
                   },
    install_requires=['colorama','setuptools','officegenerator','pillow'],
    data_files=[],
    cmdclass={ 'doxygen': Doxygen,
               'doc': Doc,
               'uninstall': Uninstall,
               'procedure': Procedure,
             },
    zip_safe=False,
    include_package_data=True
    )

_=gettext.gettext#To avoid warnings
