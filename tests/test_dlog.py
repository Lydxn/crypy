from sage.all import GF
from Crypto.Util.number import getPrime
import random
from crypy.dlog import *


def random_generator(F):
    while True:
        g = F.random_element()
        if g.is_primitive_root():
            return g

def test_dlog():
    p = getPrime(32)
    F = GF(p)
    g = random_generator(F)

    x = random.randint(1, p - 2)
    h = g**x
    assert dlog(g, h, p) == x

    xs = [random.randint(1, p - 2) for _ in range(5)]
    hs = [g**x for x in xs]
    assert dlog(g, hs, p) == xs