from math import gcd, isqrt
from shutil import which
from subprocess import check_output
from crypy.arith import iroot

__all__ = [
    'factor_cado',
    'fermat',
    'hastad',
    'rsadec',
]


def factor_cado(n, log_level='info'):
    """Factor an integer using CADO-NFS."""
    if which('cado-nfs.py') is None:
        raise FileNotFoundError(
            "'cado-nfs.py' is not installed on your system. "
            "Please install it from https://gitlab.inria.fr/cado-nfs/cado-nfs."
        )

    args = ['cado-nfs.py', str(n), '--screenlog', log_level]
    output = check_output(args).decode().strip()
    return tuple(map(int, output.split()))


def fermat(n):
    """Factor an integer using Fermat's factorization method.

    This algorithm is only efficient if `n` is known to be the product of two "close"
    factors, where "close" means roughly sqrt(n) apart. If a solution is found, it
    returns a pair of integers (a, b) such that a*b = n and a <= b.

    In the CTF context, this can be used to factor a semiprime n = p*q where
    |p-q| ~ sqrt(n).

    References:
        - https://en.wikipedia.org/wiki/Fermat%27s_factorization_method
    """
    if n < 0:
        a, b = fermat(-n)
        return (-a, b)
    if n == 0:
        return (0, 0)
    if n <= 2:
        return (1, n)
    if n % 2 == 0:
        return (2, n // 2)
    a = isqrt(n)
    if a * a == n:
        return (a, a)
    while True:
        a += 1
        b2 = a * a - n
        b = isqrt(b2)
        if b * b == b2:
            break
    return (a - b, a + b)

def hastad(e, ciphertext_modulus_pairs):
    """Decrypt an RSA ciphertext using Hastad's broadcast attack.

    Parameters:
        e: The public exponent.
        ciphertext_modulus_pairs: A list of pairs (c_i, n_i).

    Given a set of equations c_i = m^e (mod n_i), we can use the Chinese remainder
    theorem to solve for the plaintext. Depending on the size of `m`, up to `e` pairs
    of congruences is sufficient.

    Note: SageMath 9.8 and below use a slower version of crt(). For large e, it is
    highly recommended to use a newer version of Sage, or the computation may take a
    long time.
    """
    from sage.all import crt
    values, moduli = map(list, zip(*ciphertext_modulus_pairs))
    c = crt(values, moduli)
    return iroot(c, e)

def rsadec(c, *, n=None, e=None, d=None, p=None, q=None, phi=None):
    """Decrypt an RSA ciphertext c from common parameters.

    Parameters:
        c: The ciphertext to decrypt (required argument).
        n: The RSA modulus.
        e: The public exponent.
        d: The private exponent.
        p: The first prime factor of n.
        q: The second prime factor of n.
        phi: Euler's totient of n, i.e. (p-1)*(q-1).

    This routine will attempt to recover the plaintext from the given information. If
    insufficient or invalid parameters are provided, a ValueError is raised.
    """
    if p is not None and q is not None:
        if n is None:
            n = p * q
        elif p * q != n:
            raise ValueError('p*q does not equal n')
    elif n is not None:
        if p is not None:
            if n % p != 0:
                raise ValueError('p does not divide n')
            q = n // p
        elif q is not None:
            if n % q != 0:
                raise ValueError('q does not divide n')
            p = n // q
    elif phi is not None:
        if p is not None:
            if phi % (p - 1) != 0:
                raise ValueError('p-1 does not divide phi')
            q = phi // (p - 1) + 1
            n = p * q
        elif q is not None:
            if phi % (q - 1) != 0:
                raise ValueError('q-1 does not divide phi')
            p = phi // (q - 1) + 1
            n = p * q

    if p is not None and q is not None:
        if phi is None:
            phi = (p - 1) * (q - 1)
        elif (p - 1) * (q - 1) != phi:
            raise ValueError('(p-1)*(q-1) does not equal phi')

    if e is not None and phi is not None:
        if gcd(e, phi) != 1:
            raise ValueError('e and phi are not coprime')
        d = pow(e, -1, phi)

    if n is not None and d is not None:
        return pow(c, d, n)

    raise ValueError('insufficient parameters provided')