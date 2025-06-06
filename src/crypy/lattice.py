from shutil import which
from subprocess import check_output

__all__ = ['flatter']


def flatter(M, alpha=None, rhf=None, delta=None):
    """Perform lattice basis reduction on a matrix using flatter.

    flatter is currently the fastest implementation of LLL for large matrices, and can
    handle lattice bases of dimension over 1000. It is worth noting that fpylll or
    Sage's LLL may be quicker for small matrices (e.g. below dimension 100).

    References:
        - https://github.com/keeganryan/flatter
    """
    from sage.all import ZZ, matrix

    if which('flatter') is None:
        raise FileNotFoundError(
            "'flatter' is not installed on your system. "
            "Please install it from https://github.com/keeganryan/flatter."
        )

    args = ['flatter']
    if alpha is not None:
        args += ['-alpha', str(alpha)]
    if rhf is not None:
        # This flag has a similar effect to using BKZ in Sage with a custom block size,
        # but it is rather fiddly. The logic for translating the rhf into a block size
        # can be found inside src/problems/lattice_reduction/fplll_impl.cpp.
        args += ['-rhf', str(rhf)]
    if delta is not None:
        args += ['-delta', str(delta)]

    s = '[[' + ']\n['.join(' '.join(map(hex, row)) for row in M) + ']]'
    output = check_output(args, input=s.encode())
    basis = [list(map(int, row[1:-1].split(b' '))) for row in output[1:-3].split(b'\n')]
    return matrix(ZZ, basis)

def solve_ineq(M, bounds, moduli=None, algorithm='kannan', reduction=flatter):
    pass

def solve_ineq_poly(eqs, bounds, moduli=None, algorithm='kannan', reduction=flatter):
    pass