"""
Example of solving a single DLP instance with a 256-bit modulus.

Note: This doesn't work 100% of the time because CADO-NFS is buggy and prone to failure.
"""
from sage.all import GF, randint, random_prime
from crypy import dlog

def random_generator(F):
    while True:
        g = F.random_element()
        if g.is_primitive_root():
            return g

def main():
    p = random_prime(2**256)
    F = GF(p)
    g = random_generator(F)
    x = randint(1, p - 2)
    h = g**x

    print(f'{g}^x = {h} (mod {p})')

    x0 = dlog(g, h, p)
    print(f'{x0} == {x} {"❌✅"[x0 == x]}')

if __name__ == '__main__':
    main()