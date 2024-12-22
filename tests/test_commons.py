from datetime import date, datetime
from unogenerator import can_import_uno
if can_import_uno():
    from unogenerator import Range, Coord,  commons, exceptions
    from pytest import raises

    def test_coord():
        with raises(exceptions.CoordException):
            Coord(None)
        with raises(exceptions.CoordException):
            Coord(1)
        with raises(exceptions.CoordException):
            Coord("A1A")
        with raises(exceptions.CoordException):
            Coord("1")
        with raises(exceptions.CoordException):
            Coord("1A1")
        with raises(exceptions.CoordException):
            Coord("")
        with raises(exceptions.CoordException):
            Coord("A1:A2")
        with raises(exceptions.CoordException):
            Coord("Ç1:A2")
            
        Coord("A1")
        Coord("AAAAA99999")
        
        assert repr(Coord("A2"))=="Coord <A2>"
        with raises(exceptions.CoordException):
            repr(Coord(None))
        
        
        assert Coord("A1")!=Coord("A2")
        
        
        assert Coord("C3").letterPosition()==3
        assert Coord("C3").numberPosition()==3
