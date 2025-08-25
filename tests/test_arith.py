from crypy.arith import *


def test_igcd():
    assert igcd(0, 2) == 2
    assert igcd(97, 100) == 1
    assert igcd(6, 9, 12) == 3
    assert igcd(2, 4, 6, 8) == 2

def test_igcdex():
    assert igcdex(2, 3) == (1, -1, 1)
    assert igcdex(10, 12) == (2, -1, 1)
    assert igcdex(100, 2004) == (4, -20, 1)

def test_ilcm():
    assert ilcm(0, 2) == 0
    assert ilcm(97, 100) == 9700
    assert ilcm(-3, -5) == 15
    assert ilcm(1, 2, 3, 4, 5) == 60

def test_iroot():
    assert iroot(0, 1) == 0
    assert iroot(1, 1) == 1
    assert iroot(16, 2) == 4
    assert iroot(26, 2) == 5
    assert iroot(83, 4) == 3
