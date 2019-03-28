What is pdf2odt
===============

It's a script to convert pdf to LibreOffice Writer document. Pdf pages are converted as images. It uses pdftoppm from poppler to make conversion

Links
=====

Project main page
    https://github.com/turulomio/pdf2odt/

Doxygen documentation:
    http://turulomio.users.sourceforge.net/doxygen/pdf2odt/

Pypi web page:
    https://pypi.org/project/pdf2odt/

Installation and use in Linux
=============================

If you use Gentoo you can find a ebuild in https://github.com/Turulomio/myportage/tree/master/dev-python/pdf2odt

To install in other distributions, you must have poppler installed to use pdftoppm command. You can use your distribution package manager

Then just type:

`pip install pdf2odt`

Once installed you can use it typing:
    
`pdf2odt --pdf doc.pdf doc.odt`


Installation and use in Windows
===============================

You need python installed. It works with the latest version. Don't forget to add python executables to PATH, marking it in the installation process.

Then just type:

`pip install pdf2odt`

Now you have to download poppler for windows from https://blog.alivate.com.au/poppler-windows/. Uncompress the downloaded file.

Now you can use it typing in windows shell:
    
`pdf2odt --pdf doc.pdf --pdftoppm C:\Absolut\Path\To\pdftoppm.exe doc.odt`

Dependencies
============
* https://www.python.org/, as the main programming language.
* https://pypi.org/project/colorama/, to give console colors.
* https://pypi.org/project/pillow/, to manage png images.
* https://github.com/turulomio/officegenerator/, to generate odt file
* https://poppler.freedesktop.org/, to convert pdf to images using pdftoppm
* https://blog.alivate.com.au/poppler-windows/ to install poppler in windows

Changelog
=========
0.3.0
-----
  * Fixed problem with white spaces paths in windows.
  * Improved metadata information.

0.2.0
-----
  * Now works on Windows with popper for windows installation

0.1.0
-----
  * Basic functionality
