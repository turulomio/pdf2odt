What is pdf2odt
===============

'pdf2odt' is a tool developed to be able to integrate pdf files in my university notes taken with Libreoffice.

Sometimes I need to edit its content but keeping the original document. So I add the converted pages to images (anchored as character) and then insert their content as text, after going through an OCR.

This tool does not pretend to be a pdf file converter, cloning its format

It uses pdftoppm from poppler to make conversion

Links
=====

Project main page
    https://github.com/turulomio/pdf2odt/

Pypi web page:
    https://pypi.org/project/pdf2odt/

Installation and use in Linux
=============================

To install, you must have poppler installed to use pdftoppm command. You can use your distribution package manager.

You also need Libreoffice with its python bindings, because unogenerator dependency will use it

Then just type:

`pip install pdf2odt`

Once installed you can use it typing:

`pdf2odt --pdf doc.pdf doc.odt`

If you want OCR, you have to install tesseract application then you have to run 

`pdf2odt --pdf doc.pdf --tesseract doc.odt`

Installation and use in Windows
===============================

You need python installed. It works with the latest version. Don't forget to add python executables to PATH, marking it in the installation process.

Then just type:

`pip install pdf2odt`

Now you have to download poppler for windows from https://blog.alivate.com.au/poppler-windows/. Uncompress the downloaded file and add its installation directory to Windows environment path. Here you have how to do it https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/ 


Now you can use it typing in windows shell:

`pdf2odt --pdf doc.pdf doc.odt`

If you want OCR, ou have to download tesseract for windows fromm https://github.com/UB-Mannheim/tesseract/wiki. Then you have to add its installation directory to Windows environment path too.

`pdf2odt --pdf doc.pdf --tesseract doc.odt`


Dependencies
============
* https://www.python.org/, as the main programming language.
* https://pypi.org/project/colorama/, to give console colors.
* https://github.com/turulomio/unogenerator/, to generate odt file.
* https://poppler.freedesktop.org/, to convert pdf to images using pdftoppm.
* https://blog.alivate.com.au/poppler-windows/ to install poppler in windows.
* https://pypi.org/project/tqdm, to show beautyful progress bars.
* https://github.com/tesseract-ocr/, for OCR support.

Changelog
=========
1.0.0 (2024-12-22)
------------------
  * Migrated to unogenerator
  * Updated to poetry

0.7.0
-----
  * Fixed bug with tesseract parameter position. Thanks @maxlem-neuralium 
  * Now temporal files are generated with tempfile module.

0.6.0
-----
  * Tesseract language is now showed in output
  * Now pdf2odt validates PDF document

0.5.0
-----
  * Now pdf2odt detects if tesseract language selected is supported.

0.4.0
-----
  * Added OCR support with tesseract
  * Now uses process concurrency and shows a progress bar

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
