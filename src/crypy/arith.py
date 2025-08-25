from gmpy2 import iroot as _iroot
from functools import reduce
import math

__all__ = [
    'igcd',
    'igcdex',
    'ilcm',
    'iroot',
]


def igcd(*a):
    """Compute the greatest common divisor of two or more integers."""
    return reduce(math.gcd, a)

def igcdex(a, b):
    """Return (g, x, y) such that g = x*a + y*b = gcd(a, b)."""
    x0, x1 = 1, 0
    y0, y1 = 0, 1
    while b != 0:
        q, r = divmod(a, b)
        x1, x0 = x0 - q * x1, x1
        y1, y0 = y0 - q * y1, y1
        a, b = b, r
    return a, x0, y0

def ilcm(*a):
    """Compute the least common multiple of two or more integers."""
    return reduce(math.lcm, a)

def iroot(y, n):
    """Return the floor of y^(1/n)."""
    return int(_iroot(y, n)[0])
