from Crypto.Util.number import getPrime, isPrime
from random import randrange
import pytest
from crypy.rsa import *


def test_fermat():
    # edge cases
    assert fermat(-10) == (-2, 5)
    assert fermat(-2) == (-1, 2)
    assert fermat(-1) == (-1, 1)
    assert fermat(0) == (0, 0)
    assert fermat(1) == (1, 1)

    # small cases
    for n in range(2, 120):
        a, b = fermat(n)
        assert a * b == n and 1 <= a <= b
        if not isPrime(n):
            assert a != 1

    # large case
    p, q = 10**100 + 267, 10**100 + 10**51 + 233
    assert fermat(p * q) == (p, q)

def test_hastad():
    e = 3
    m = randrange(2**128)
    ciphertext_modulus_pairs = []
    for _ in range(e + 1):
        p, q = getPrime(64), getPrime(64)
        n = p * q
        c = pow(m, e, n)
        ciphertext_modulus_pairs.append((c, n))
    assert hastad(e, ciphertext_modulus_pairs) == m

def test_rsadec():
    p, q = getPrime(64), getPrime(64)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 0x10001
    d = pow(e, -1, phi)
    m = randrange(n)
    c = pow(m, e, n)

    assert rsadec(c, d=d, p=p, q=q) == m
    assert rsadec(c, d=d, p=p, phi=phi) == m
    assert rsadec(c, d=d, q=q, phi=phi) == m
    assert rsadec(c, e=e, p=p, phi=phi) == m
    assert rsadec(c, e=e, q=q, phi=phi) == m
    assert rsadec(c, n=n, d=d) == m
    assert rsadec(c, n=n, e=e, phi=phi) == m
    assert rsadec(c, n=n, e=e, p=p) == m
    assert rsadec(c, n=n, e=e, q=q) == m

    with pytest.raises(ValueError):
        rsadec(c, n=7, d=d, p=2, q=3)
    with pytest.raises(ValueError):
        rsadec(c, n=7, d=d, p=2)
    with pytest.raises(ValueError):
        rsadec(c, n=7, d=d, q=3)
    with pytest.raises(ValueError):
        rsadec(c, d=d, p=3, phi=5)
    with pytest.raises(ValueError):
        rsadec(c, d=d, q=3, phi=5)
    with pytest.raises(ValueError):
        rsadec(c, d=d, p=3, q=3, phi=5)

    with pytest.raises(ValueError):
        rsadec(c, n=n, e=e)
    with pytest.raises(ValueError):
        rsadec(c, n=n, phi=phi)
    with pytest.raises(ValueError):
        rsadec(c, d=d)
    with pytest.raises(ValueError):
        rsadec(c, e=e, d=d, p=p)
