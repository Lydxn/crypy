from functools import partial
from shutil import which
from subprocess import check_output

__all__ = [
    'BKZ',
    'Flatter',
    'LLL',
    'SP',
    'SPC',
    'SymPoly',
    'SymPolyConstraint',
    'bkz',
    'cvp_babai',
    'cvp_kannan',
    'flatter',
    'lll',
    'solve_lineq',
    'solve_lineq_poly',
]


class SymPoly:
    def __init__(self, poly, modulus=None):
        from sage.all import ZZ

        if modulus is not None:
            if not isinstance(modulus, int):
                raise ValueError('modulus must be an integer')
            if modulus <= 0:
                raise ValueError('modulus must be positive')

        self.poly = poly.change_ring(ZZ)
        self.modulus = modulus

        if self.modulus is not None:
            self.poly %= modulus

    def __eq__(self, other):
        return SymPolyConstraint(self, other)

    def __mod__(self, modulus):
        self._check_compatible_modulus(modulus)
        return SymPoly(self.poly, modulus)

    def __add__(self, other):
        if isinstance(other, SymPoly):
            self._check_compatible_modulus(other.modulus)
            other = other.poly
        return SymPoly(self.poly + other, self.modulus)

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, SymPoly):
            self._check_compatible_modulus(other.modulus)
            other = other.poly
        return SymPoly(self.poly - other, self.modulus)

    def __rsub__(self, other):
        return SymPoly(other - self.poly, self.modulus)

    def __repr__(self):
        return self.poly.__repr__()

    def _check_compatible_modulus(self, modulus):
        if self.modulus is not None and modulus != self.modulus:
            raise ValueError('incompatible modulus')


class SymPolyConstraint:
    def __init__(self, lhs, rhs):
        is_lhs_poly = isinstance(lhs, SP)
        is_rhs_poly = isinstance(rhs, SP)
        if is_lhs_poly and is_rhs_poly:
            if lhs.modulus != rhs.modulus:
                raise ValueError('incompatible modulus')
            self.poly = (lhs - rhs).poly
            self.lb = self.ub = 0
            self.modulus = lhs.modulus
        elif not is_lhs_poly and not is_rhs_poly:
            raise ValueError('at least one argument must be of type SymPoly')
        else:
            if is_rhs_poly:
                # always swap so that `lhs` is a SymPoly and `rhs` is not
                lhs, rhs = rhs, lhs
            self.modulus = lhs.modulus
            if isinstance(rhs, int):
                c = lhs.poly.constant_coefficient()
                self.poly = lhs.poly - c
                self.lb = self.ub = rhs + c
            elif isinstance(rhs, tuple) and len(rhs) == 2:
                if not isinstance(rhs[0], int) or not isinstance(rhs[1], int):
                    raise ValueError('bound values must be integers')
                if rhs[0] > rhs[1]:
                    raise ValueError('lower bound cannot be greater than upper bound')
                c = lhs.poly.constant_coefficient()
                self.poly = lhs.poly - c
                self.lb = rhs[0] + c
                self.ub = rhs[1] + c
            else:
                raise TypeError('left or right hand side is invalid')

    def __repr__(self):
        if self.lb == self.ub:
            s = f'{self.poly} == {self.lb}'
        else:
            s = f'{self.poly} == {self.lb}..{self.ub}'
        if self.modulus is not None:
            s += f' (mod {self.modulus})'
        return s

SP = SymPoly
SPC = SymPolyConstraint


def flatter(M, alpha=None, rhf=None, delta=None):
    """Perform lattice basis reduction using flatter.

    flatter is currently the fastest implementation of LLL for large matrices, and can
    handle lattice bases of dimension over 1000. It is worth noting that fpylll or
    Sage's LLL may be quicker for small matrices (e.g. below dimension 50).

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

def lll(M, *args, **kwargs):
    """Perform lattice basis reduction using the LLL algorithm."""
    return M.LLL(*args, **kwargs)

def bkz(M, *args, **kwargs):
    """Perform lattice basis reduction using the BKZ algorithm."""
    return M.BKZ(*args, **kwargs)

# convenience funcs for the reduce parameter in solve_lineq() -- for example you can do
# `solve_lineq(..., reduce=BKZ(20))` instead of `reduce=lambda x: x.BKZ(block_size=20)`.
Flatter = lambda rhf=None, /, *args, **kwargs: partial(flatter, rhf=rhf, *args, **kwargs)
LLL = lambda *args, **kwargs: partial(lll, *args, **kwargs)
BKZ = lambda block_size=10, /, *args, **kwargs: \
    partial(bkz, block_size=block_size, *args, **kwargs)

def cvp_kannan(M, target, reduce=flatter, q=None):
    """Solve the closest vector problem using Kannan embedding.

    Parameters:
        M: An integer matrix representing the lattice basis (as row vectors).
        target: The target vector.
        reduce (optional): The lattice reduction function, the default uses flatter.
        q (optional): The embedding factor, the default chooses q = |target|.
    """
    from sage.all import ZZ, block_matrix, matrix, vector

    target = vector(ZZ, target)
    if q is None:
        q = target.norm().round() or 1
    L = block_matrix(ZZ, [[M, 0], [-matrix(target), q]])
    for row in reduce(L):
        if row[-1] < 0:
            row = -row
        if row[-1] == q:
            return row[:-1] + target

def cvp_babai(M, target, reduce=flatter):
    """Solve the closest vector problem using Babai's nearest plane algorithm.

    Parameters:
        M: An integer matrix representing the lattice basis (as row vectors).
        target: The target vector.
        reduce (optional): The lattice reduction function, the default uses flatter.
    """
    from sage.all import ZZ, vector

    target = vector(ZZ, target)
    L = reduce(M)
    G = L.gram_schmidt()[0]
    diff = target
    for i in range(G.nrows() - 1, -1, -1):
        diff -= L[i] * ((diff * G[i]) / (G[i] * G[i])).round()
    return target - diff

def solve_lineq(M, bounds, algorithm='kannan', reduce=flatter, q=None):
    """Find an integer vector `x` that satisfies `M*x = t` and return `t`, where the
    target vector `t` is constrained by a set of bounds.

    Note: This function does not return `x`, but you can apply Kannan embedding on the
    matrix to extract it.

    Parameters:
        M: An integer matrix representing the lattice basis (as row vectors).
        bounds: A list of (lower_bound, upper_bound) pairs, which constrain the target
            vector `t`.
        algorithm (optional): The CVP algorithm used, either 'kannan' or 'babai'.
        reduce (optional): The lattice reduction function, the default uses flatter.
        q: The embedding factor, only applies when the algorithm uses Kannan.
    """
    from sage.all import ZZ, matrix

    n, m = M.dimensions()
    if any(lb > ub for lb, ub in bounds):
        raise ValueError('bounds are invalid because lb > ub')
    if len(bounds) != m:
        raise ValueError('len(bounds) is not equal to number of columns in M')

    target = [lb + ub for lb, ub in bounds]
    deltas = [ub - lb for lb, ub in bounds]
    scale = max(deltas)
    weights = [scale // d if d != 0 else scale * n for d in deltas]

    B = matrix(ZZ, 2 * M)
    for i in range(m):
        B[:, i] *= weights[i]
        target[i] *= weights[i]

    if algorithm == 'kannan':
        L = cvp_kannan(B, target, reduce=reduce, q=q)
    elif algorithm == 'babai':
        L = cvp_babai(B, target, reduce=reduce)
    else:
        raise ValueError("invalid algorithm, must either be 'kannan' or 'babai'")

    for i in range(m):
        L[i] /= 2 * weights[i]
    return L

def solve_lineq_poly(relations, algorithm='kannan', reduce=flatter, q=None):
    from sage.all import Sequence, ZZ, matrix

    """Solve a system of integer linear inequalities using lattice reduction.

    Parameters:
        relations: A sequence of SymPolyConstraint equations.
        algorithm (optional): The CVP algorithm used, either 'kannan' or 'babai'.
        reduce (optional): The lattice reduction function, the default uses flatter.
        q: The embedding factor, only applies when the algorithm uses Kannan.
    """
    polys, moduli, bounds = [], [], []
    for r in relations:
        polys.append(r.poly)
        moduli.append(r.modulus)
        bounds.append((r.lb, r.ub))

    M, _ = Sequence(polys).coefficients_monomials(sparse=False)
    M = M.transpose()
    n, m = M.dimensions()

    mod_indices = [i for i in range(m) if moduli[i] is not None]
    N = matrix(ZZ, len(mod_indices), m)
    for i, j in enumerate(mod_indices):
        N[i, j] = moduli[j]

    M = M.stack(N)
    return solve_lineq(M, bounds, algorithm=algorithm, reduce=reduce, q=q)