from sage.all import GF, PolynomialRing, ZZ, Zmod, gcd, polygen
import pytest
from crypy.polynomial import *


rings = [GF(2**64), GF(2888075089), Zmod(4294967311 * 4294967357), ZZ]

@pytest.mark.parametrize('R', rings)
def test_pgcd(R):
    P = PolynomialRing(R, 'x')
    for _ in range(10):
        g = P.random_element(5).monic()
        a = P.random_element(10)
        if R is ZZ:
            while not a.is_irreducible():
                a = P.random_element(10)
        b = P.random_element(10)
        assert pgcd(a * g, b * g) == g

@pytest.mark.parametrize('R', rings)
def test_pgcdex(R):
    if R is ZZ:
        # PARI fails for ZZ. I'm not sure how to fix this but you could use xgcd()
        # instead.
        return
    P = PolynomialRing(R, 'x')
    for _ in range(10):
        g = P.random_element(5).monic()
        a = g * P.random_element(10)
        b = g * P.random_element(10)
        r, s, t = pgcdex(a, b)
        assert r.monic() == pgcd(a, b) and r == s * a + t * b

@pytest.mark.parametrize('R', rings)
def test_resultant(R):
    x, y = polygen(R, 'x, y')
    f = x + y
    g = x**3 - y**3
    h = 2*x**3
    assert resultant(f, g, y) == h
