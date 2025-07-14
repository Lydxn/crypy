from sage.all import ZZ, matrix, random_matrix, random_vector
from sage.modules.free_module_integer import IntegerLattice
from secrets import randbits, randbelow
import pytest
from crypy.lattice import *


@pytest.mark.parametrize('reduce', [flatter, lll, bkz])
def test_reduce(reduce):
    M = random_matrix(ZZ, 4, 4)
    actual = next(row for row in reduce(M) if row != 0)
    expected = IntegerLattice(M).shortest_vector()
    assert abs(actual.norm() - expected.norm()) < 2.5

@pytest.mark.parametrize('cvp', [cvp_kannan, cvp_babai])
def test_cvp(cvp):
    M = random_matrix(ZZ, 4, 4)
    target = random_vector(ZZ, 4)
    actual = cvp(M, target)
    expected = IntegerLattice(M).approximate_closest_vector(target)
    assert abs(actual.norm() - expected.norm()) < 2.5

@pytest.mark.parametrize('algorithm', ['kannan', 'babai'])
def test_solve_lineq(algorithm):
    p = randbits(128)
    a, b = randbelow(p), randbelow(p)
    x, y = randbits(40), randbits(40)
    c = (a * x + b * y) % p
    M = matrix(ZZ, [
        [a, 1, 0],
        [b, 0, 1],
        [p, 0, 0],
    ])
    bounds = [(c, c)] + [(0, 2**40)] * 2
    sol = solve_lineq(M, bounds, algorithm=algorithm)
    assert tuple(map(int, sol)) == (c, x, y)

@pytest.mark.parametrize('algorithm', ['kannan', 'babai'])
def test_solve_lineq_poly(algorithm):
    from sage.all import polygen

    # Example 1: a*x + y = c (mod p)
    p = randbits(128)
    a = randbelow(p)
    x, y = randbits(40), randbits(40)
    c = (a * x + y) % p

    xx = polygen(ZZ, 'xx')
    relations = [
        SP(xx) == (0, 2**40),
        SP(c - a * xx) % p == (0, 2**40),
    ]
    sol = solve_lineq_poly(relations, algorithm=algorithm)
    assert tuple(map(int, sol)) == (x, y)

    # Example 2: a*x + b*y = c (mod p)
    p = randbits(128)
    a, b = randbelow(p), randbelow(p)
    x, y = randbits(40), randbits(40)
    c = (a * x + b * y) % p
    xx, yy = polygen(ZZ, 'xx, yy')
    relations = [
        SP(a * xx + b * yy) % p == c,
        SP(xx) == (0, 2**40),
        SP(yy) == (0, 2**40),
    ]
    sol = solve_lineq_poly(relations, algorithm=algorithm)
    assert tuple(map(int, sol)) == (c, x, y)