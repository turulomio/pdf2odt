from unogenerator import can_import_uno
if can_import_uno():
    from pdf2odt.core import main_command
    from os import path,  remove
    from unogenerator import ODT_Standard
    
    def test_main(libreoffice_server):
        # Creates a pdf
        with ODT_Standard(server=libreoffice_server) as doc:
            doc.addParagraph("Hello world!")
            doc.export_pdf("main.pdf")
            
        assert path.exists("main.pdf")
        
        main_command("main.pdf",  "eng",  300,  True,  "main.odt")
        
        assert path.exists("main.odt")
        
        remove("main.pdf")
        remove("main.odt")
        
