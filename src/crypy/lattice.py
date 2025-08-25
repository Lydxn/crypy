from functools import partial
from shutil import which
from subprocess import check_output

__all__ = [
    'BKZ',
    'CVPSolver',
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
    'get_cvp_weights',
    'lll',
    'ortho_lattice',
    'solve_lineq',
    'solve_lineq_poly',
    'spolys_to_matrix',
]


class SymPoly:
    """Represents a linear symbolic polynomial over the integers.

    This class is used to define symbolic expressions used in the linear inequality
    solvers. Here are some examples of its usage:

    >>> SP(3*x + 4*y)
    3*x + 4*y
    >>> 3*SP(x) + 4*SP(y)
    3*x + 4*y
    >>> SP(x*y)
    ...
    ValueError: polynomial is not linear
    """

    def __init__(self, poly, modulus=None):
        from sage.all import ZZ

        if modulus is not None:
            if not isinstance(modulus, int):
                raise ValueError('modulus must be an integer')
            if modulus <= 0:
                raise ValueError('modulus must be positive')

        if poly.degree() > 1:
            raise ValueError('polynomial is not linear')

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

    def __mul__(self, other):
        if not isinstance(other, int):
            raise ValueError('can only multiply SymPoly by an integer')
        return SymPoly(other * self.poly, self.modulus)

    __rmul__ = __mul__

    def __pos__(self):
        return SymPoly(self.poly, self.modulus)

    def __neg__(self):
        return SymPoly(-self.poly, self.modulus)

    def __repr__(self):
        return self.poly.__repr__()

    def _check_compatible_modulus(self, modulus):
        if self.modulus is not None and modulus != self.modulus:
            raise ValueError('incompatible modulus')


class SymPolyConstraint:
    """Represents a linear symbolic polynomial constraint.

    This class is used to define symbolic constraints used in the linear inequality
    solvers. Defining constraints can be done by applying `==` to a symbolic polynomial.

    See examples below for how this works:

    >>> SP(3*x + 4*y)
    3*x + 4*y
    >>> SP(3*x + 4*y) == 1
    3*x + 4*y == 1
    >>> SP(3*x + 4*y) % 6 == 1
    3*x + 4*y == 1 (mod 6)
    >>> SP(3*x + 4*y) % 6 == (3, 5)
    3*x + 4*y == 3..5 (mod 6)
    """

    def __init__(self, lhs, rhs):
        # Swap so that `lhs` is a SymPoly and `rhs` is a constant/range term
        if isinstance(rhs, SP):
            lhs, rhs = rhs, lhs
        if isinstance(rhs, SP):
            raise ValueError('right-hand side must be a constant term (int or tuple)')
        if not isinstance(lhs, SP):
            raise ValueError('at least one argument must be of type SymPoly')

        self.spoly = lhs
        if isinstance(rhs, int):
            self.lb = self.ub = rhs
        elif isinstance(rhs, tuple) and len(rhs) == 2:
            if not isinstance(rhs[0], int) or not isinstance(rhs[1], int):
                raise ValueError('bound values must be integers')
            if rhs[0] > rhs[1]:
                raise ValueError('lower bound cannot be greater than upper bound')
            self.spoly = lhs
            self.lb, self.ub = rhs
        else:
            raise TypeError('left or right hand side is invalid')

    def __repr__(self):
        if self.lb == self.ub:
            s = f'{self.spoly} == {self.lb}'
        else:
            s = f'{self.spoly} == {self.lb}..{self.ub}'
        if self.spoly.modulus is not None:
            s += f' (mod {self.spoly.modulus})'
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
    return M.dense_matrix().LLL(*args, **kwargs)

def bkz(M, *args, **kwargs):
    """Perform lattice basis reduction using the BKZ algorithm."""
    return M.dense_matrix().BKZ(*args, **kwargs)

# convenience funcs for the reduce parameter in solve_lineq() -- for example you can do
# `solve_lineq(..., reduce=BKZ(20))` instead of `reduce=lambda x: x.BKZ(block_size=20)`.
Flatter = lambda rhf=None, /, *args, **kwargs: partial(flatter, rhf=rhf, *args, **kwargs)
LLL = lambda *args, **kwargs: partial(lll, *args, **kwargs)
BKZ = lambda block_size=10, /, *args, **kwargs: \
    partial(bkz, block_size=block_size, *args, **kwargs)

_default_reduce = flatter

def cvp_kannan(M, target, reduce=_default_reduce, q=None):
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

def cvp_babai(M, target, reduce=_default_reduce):
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

def spolys_to_matrix(spolys):
    """Transform a sequence of symbolic polynomials to a matrix of monomial coefficients
    and a vector of constant coefficients.

    If a polynomial has a modulus, a "dummy" row is added to represent `x (mod p)` as
    `x - dummy*p`. This is helpful in constructing lattice attacks.

    The function returns a tuple (A, c), representing the coefficient matrix and vector,
    respectively.
    """
    from sage.all import Sequence, ZZ, matrix, vector

    polys, moduli = [], []
    for sp in spolys:
        polys.append(sp.poly)
        moduli.append(sp.modulus)

    # `.coefficients_monomials()` does not exist for univariate polynomials
    if polys[0].parent().ngens() == 1:
        M = matrix(ZZ, [poly.list()[::-1] for poly in polys])
    else:
        M, v = Sequence(polys).coefficients_monomials(sparse=False)
        if v[-1] != 1:
            M = M.augment(vector(ZZ, M.nrows()))
    A, c = M[:, :-1], M.column(-1)
    A = A.transpose()
    n, m = A.dimensions()

    mod_indices = [i for i in range(m) if moduli[i] is not None]
    N = matrix(ZZ, len(mod_indices), m)
    for i, j in enumerate(mod_indices):
        N[i, j] = moduli[j]

    return A.stack(N), c

def get_cvp_weights(M, bounds):
    n, m = M.dimensions()

    if any(lb > ub for lb, ub in bounds):
        raise ValueError('bounds are invalid because lb > ub')
    if len(bounds) != m:
        raise ValueError('len(bounds) is not equal to number of columns in M')

    deltas = [ub - lb for lb, ub in bounds]
    scale = max(deltas) or M.det()
    return [scale // d if d != 0 else scale * n for d in deltas]

def solve_lineq(M, bounds, algorithm='kannan', reduce=_default_reduce, check=False, q=None):
    """Find an integer vector `x` that satisfies `M*x = t` and return the target vector
    `t`, where `t` is constrained by a list of bounds.

    Note: The bounds are *soft*. LLL will try its best, but the returned vector may not
    respect the bounds.

    Parameters:
        M: An integer matrix representing the lattice basis (as row vectors).
        bounds: A list of (lower_bound, upper_bound) pairs, which constrain the target
            vector `t`.
        algorithm (optional): The CVP algorithm used, either 'kannan' or 'babai'.
        reduce (optional): The lattice reduction function, the default uses flatter.
        check (optional): Return None if the result is not within the bounds.
        q: The embedding factor, only applies when the algorithm uses Kannan.
    """
    from sage.all import ZZ, matrix

    bounds = [b if isinstance(b, tuple) else (b, b) for b in bounds]
    target = [lb + ub for lb, ub in bounds]
    weights = get_cvp_weights(M, bounds)

    m = M.ncols()
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

    if not check or all(lb <= x <= ub for x, (lb, ub) in zip(L, bounds)):
        return L
    return None

def solve_lineq_poly(relations, algorithm='kannan', reduce=_default_reduce, check=False, q=None):
    """Solve a system of integer linear inequalities using lattice reduction.

    Parameters:
        relations: A sequence of SymPolyConstraint equations.
        algorithm (optional): The CVP algorithm used, either 'kannan' or 'babai'.
        reduce (optional): The lattice reduction function, the default uses flatter.
        check (optional): Return None if the result is not within the bounds.
        q: The embedding factor, only applies when the algorithm uses Kannan.
    """
    spolys = [r.spoly for r in relations]
    A, cs = spolys_to_matrix(spolys)
    bounds = [(r.lb - c, r.ub - c) for r, c in zip(relations, cs)]
    sol = solve_lineq(A, bounds, algorithm=algorithm, reduce=reduce, check=check, q=q)
    return sol + cs

def ortho_lattice(M, mod=None, reduce=_default_reduce):
    """Compute a short orthogonal basis of the matrix.

    For every row vector in the returned matrix `B`, the equation `M*B = 0` holds.

    Parameters:
        M: An integer matrix of column vectors.
        mod (optional): The modulus over which the orthogonal lattice is computed.
        reduce (optional): The lattice reduction function, the default uses flatter.
    """
    from sage.all import ZZ, block_matrix, diagonal_matrix, matrix

    M = matrix(ZZ, M)
    n, m = M.dimensions()
    if mod is None:
        w = max(max(M)) * 2**10
        B = block_matrix(ZZ, [[M.T, 1]])
    else:
        w = mod
        B = block_matrix(ZZ, [[M.T, 1], [mod, 0]])
    W = diagonal_matrix(ZZ, [w] * n + [1] * m)
    L = reduce(B * W) / W
    B = []
    for row in L:
        if row[:n] == 0:
            B.append(row[n:])
    return matrix(ZZ, B)


class CVPSolver:
    """Linear inequality solver for efficient target queries.

    This class can be utilized to CVP solve queries with a fixed basis, but different
    target vectors efficiently. It keeps track of a weight cache to avoid doing extra
    lattice reductions whenever possible.

    If the relative sizes of the bounds are constant across queries, then we can use
    solve them efficiently using Babai's algorithm + precomputed LLL, since the overall
    basis doesn't change.
    """
    def __init__(self, basis_or_spolys, reduce=_default_reduce):
        from sage.all import ZZ, matrix

        # The solver accepts either a matrix or a sequence of symbolic polynomials. If
        # it can't be cast to a Sage matrix then assume it is the latter...
        try:
            self.M = matrix(ZZ, basis_or_spolys)
        except Exception:
            self.M = spolys_to_matrix(basis_or_spolys)
        self._weight_cache = {}
        self.reduce = reduce

    def solve(self, bounds, check=False):
        from sage.all import ZZ, matrix, vector

        m = self.M.ncols()
        bounds = [b if isinstance(b, tuple) else (b, b) for b in bounds]
        deltas = tuple(ub - lb for lb, ub in bounds)
        entry = self._weight_cache.get(deltas)
        if entry is None:
            weights = get_cvp_weights(self.M, bounds)
            B = matrix(ZZ, 2 * self.M)
            for i in range(m):
                B[:, i] *= weights[i]
            L = self.reduce(B)
            G = L.gram_schmidt()[0]
            C = [v / (v * v) for v in G]
            self._weight_cache[deltas] = (L, C, weights)
        else:
            L, C, weights = entry

        target = vector(ZZ, [(lb + ub) * w for (lb, ub), w in zip(bounds, weights)])
        L = self._babai_step(L, C, target)
        for i in range(m):
            L[i] /= 2 * weights[i]

        if not check or all(lb <= x <= ub for x, (lb, ub) in zip(L, bounds)):
            return L
        return None

    @staticmethod
    def _babai_step(L, C, target):
        diff = target
        for i in range(len(C) - 1, -1, -1):
            diff -= L[i] * (diff * C[i]).round()
        return target - diff
