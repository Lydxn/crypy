from shutil import which
from subprocess import check_output

__all__ = [
    'dlog',
    'dlog_cado',
    'dlog_pari',
]


def dlog(g, h, p, debug='info', small_bound=2**64):
    """Compute the discrete log in GF(p).

    Parameters:
        g: The base generator.
        h: One, or a sequence of target values of the exponentiation mod p.
        p: The prime modulus.
        debug: The debug mode for CADO-NFS; one of 'warn', 'info', 'command' or 'debug'
        (in increasing order of verbosity).
        small_bound: The maximum subgroup size at which to use the general algorithm.
    """
    from sage.all import crt, factor, prod

    is_sequence = hasattr(h, '__iter__')
    if not is_sequence:
        h = [h]

    order = p - 1
    factors = factor(order)
    ells = []
    for pi, ei in factors:
        if pi > small_bound:
            ells.append(pi**ei)
            print((pi, ei))

    if not ells:
        xs = [dlog_pari(g, h0, p, order, factors) for h0 in h]
    else:
        results = [dlog_cado(g, h, p, ell, debug=debug) for ell in ells]
        x_larges = [crt(result, ells) for result in map(list, zip(*results))]
        P = prod(ells)
        Q = order // P
        Qfac = factor(Q)
        xs = []
        for h0, x_large in zip(h, x_larges):
            x_small = dlog_pari(g, h0, p, Q, Qfac)
            x = crt([x_large, x_small], [P, Q])
            xs.append(x)
    return xs if is_sequence else xs[0]


def dlog_cado(g, h, p, ell, debug='info'):
    """Compute the discrete log in GF(p) using CADO-NFS.

    Parameters:
        g: The base generator.
        h: One, or a sequence of target values of the exponentiation mod p.
        p: The prime modulus.
        ell: The subgroup order in which the discrete log is computed.
        debug: The debug mode for CADO-NFS; one of 'warn', 'info', 'command' or 'debug'
        (in increasing order of verbosity).

    The function solves the equation g^x = h (mod p) and returns x mod ell, where
    ell must be a prime factor of p-1. Only use this function if you want more
    fine-grained control over solving the discrete log with CADO-NFS. Otherwise you
    probably want to call dlog() instead.

    If p-1 splits into several subgroups, CADO-NFS is only able to solve for the large
    subgroups. Usually this means `ell` is the largest prime factor, and the rest of
    them must be computed separately using Pohlig-Hellman.

    References:
        - https://gitlab.inria.fr/cado-nfs/cado-nfs
    """
    if which('cado-nfs.py') is None:
        raise FileNotFoundError(
            "'cado-nfs.py' is not installed on your system. "
            "Please install it from https://gitlab.inria.fr/cado-nfs/cado-nfs."
        )

    is_sequence = hasattr(h, '__iter__')
    if not is_sequence:
        h = [h]

    targets = ','.join(map(str, [g, *h]))
    args = [
        'cado-nfs.py', '-dlp', '-ell', str(ell), f'target={targets}', str(p),
        '--screenlog', debug,
    ]
    output = check_output(args).decode().strip()
    logg, *loghs = list(map(int, output.split(',')))
    xs = [lg * pow(logg, -1, ell) % ell for lg in loghs]
    return xs if is_sequence else xs[0]

def dlog_pari(g, h, p, ell=None, ellfac=None):
    """Compute the discrete log in GF(p) using PARI.

    Parameters:
        g: The base generator.
        h: The target value of the exponentiation mod p.
        p: The prime modulus.
        ell: The subgroup order in which the discrete log is computed (p-1 by default).
        ellfac: The prime factors of ell as a list of (p_i, e_i) pairs (optional).

    The function solves the equation g^x = h (mod p) and returns x mod ell, where
    ell must be a factor (not necessarily prime) of p-1.

    Sage basically does the same thing, but doesn't allow you to specify a subgroup
    order `ell`, which could be useful in some cases.

    References:
        - https://en.wikipedia.org/wiki/Pohlig%E2%80%93Hellman_algorithm
    """
    from sage.all import Factorization, GF, factor, pari, prod

    order = p - 1
    if ell is None:
        ell = order
    if order % ell != 0:
        raise ValueError('ell must divide p-1')
    if ellfac is None:
        ellfac = factor(ell)
    else:
        ellfac = Factorization(ellfac)
        assert prod(p_i**e_i for p_i, e_i in ellfac) == ell

    F = GF(p)
    gg = F(g)**(order // ell)
    hh = F(h)**(order // ell)
    return int(pari.znlog(hh, gg, [ell, ellfac]))