What is pdf2odt
===============

It's a script to convert pdf to LibreOffice Writer document. Pdf pages are converted as images. It uses pdftoppm from poppler to make conversion

Usage
=====

`pdf2odt --pdf doc.pdf doc.odt`

Links
=====

Doxygen documentation:
    http://turulomio.users.sourceforge.net/doxygen/pdf2odt/

Pypi web page:
    https://pypi.org/project/pdf2odt/

Installation in Linux
=====================

If you use Gentoo you can find a ebuild in https://github.com/Turulomio/myportage/tree/master/dev-python/pdf2odt

To install in other distributions, you must have poppler installed to use pdftoppm command. You can use your distribution package manager

Then just type:

`pip install pdf2odt`

Dependencies
============
* https://www.python.org/, as the main programming language.
* https://pypi.org/project/colorama/, to give console colors.
* https://github.com/turulomio/officegenerator/, to generate odt file
* https://poppler.freedesktop.org/, to convert pdf to images using pdftoppm

Changelog
=========
0.1.0
-----
  * Basic functionality
