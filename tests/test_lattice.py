from random import getrandbits, randrange
from crypy.lattice import *


def test_flatter():
    # a*x + b*y = c (mod p)
    p = getrandbits(128)
    a, b = [randrange(p) for _ in range(2)]
    x, y = [getrandbits(32) for _ in range(2)]
    c = a * x + b * y
    W = 2**128
    M = [
        [ a*W, 1, 0, 0],
        [ b*W, 0, 1, 0],
        [-c*W, 0, 0, W],
        [ p*W, 0, 0, 0],
    ]
    L = flatter(M)
    sol = [row for row in L if row[0] == 0 and abs(row[-1]) == W][0]
    if sol[-1] < 0:
        sol *= -1
    xx, yy = int(sol[1]) % p, int(sol[2]) % p
    assert xx == x and yy == y
