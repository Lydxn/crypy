"""
Solve script for "Chinese Rabinder Theorem" from Season V, US Cyber Open.
"""
from sage.all import *
from crypy import *
from itertools import product
from tqdm import tqdm

n = 30327208759781412025136331048643419536910103237132356122012246111636453702769363409081910784093069558218111
c = 17809769080654903649334892184111600681027552797084733634899402165936938957467437130366159467052858323916324
primes = [523, 547, 563, 571, 587, 599, 607, 619, 631, 643, 647, 659, 683, 691, 719, 727, 739, 743, 751, 787, 811, 823, 827, 839, 859, 863, 883, 887, 907, 911, 919, 947, 967, 971, 983, 991, 1019]
assert n == prod(primes)

roots = [int(GF(p)(c).sqrt()) * (n // p) * pow(n // p, -1, p) for p in primes]
k = len(primes)

g = 10  # no. of guess bits
l = 35  # guess length of flag

M = block_matrix(ZZ, [[matrix(roots[g:] + [256]).T, 1], [n, 0]])
cvp = CVPSolver(M)

T = b2l(b'SVUSCG{' + b'\x00' * l + b'}')
for d in tqdm(product([1, -1], repeat=g)):
    ofs = sum(x * y for x, y in zip(roots[:g], d))
    bounds = [T - ofs] + [(-1, 1)] * (k - g) + [(0, 256**l)]
    sol = cvp.solve(bounds)
    flag = l2b(abs(sol[-1]))
    if flag.isascii():
        print('SVUSCG{%s}' % flag.decode())