from sage.all import *
from crypy import *
from itertools import product
import re
import string

mod = 13**37
l = 23
g = 3

T = b2l(b'SEE{' + b'\x00'*l + b'}')
B = [pow(256, l - i, mod) for i in range(l)]
M = block_matrix(ZZ, [[matrix(B[g:]).T, 1], [mod, 0]])

alphabet = list(map(ord, string.ascii_letters + string.digits + '_'))

cvp = CVPSolver(M, reduce=BKZ(45))
for guess in map(bytes, product(alphabet, repeat=g)):
    s = sum(x * y for x, y in zip(guess, B[:g]))
    target = (-T - s) % mod
    bounds = [(target, target)] + [(48, 122)] * (l - g)
    sol = cvp.solve(bounds)
    if sol is None or sol[0] != target or not all(48 <= c <= 122 for c in sol[1:]):
        continue
    flag = guess + bytes(sol[1:])
    assert b2l(b'SEE{' + flag + b'}') % mod == 0
    if re.fullmatch(rb'\w{23}', flag):
        print('found:', flag)
        break
    else:
        print('candidate:', flag)