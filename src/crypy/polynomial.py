__all__ = [
    'pgcd',
    'pgcdex',
    'resultant',
]


def pgcd(f, g):
    """Compute the greatest common divisor of two polynomials.

    In Sage 10.6 or below, gcd() fails for composite rings implemented by NTL. This
    function seeks to handle this special case using the PR from [1]. It should be fixed
    in future versions, but we'll keep this workaround for now.

    References:
        - https://github.com/sagemath/sage/pull/40017 [1]
    """
    P = f.parent()
    h = P(f._pari_with_name().gcd(g._pari_with_name()))
    c = h.leading_coefficient()
    if c != P(0):
        h /= c
    return h

def pgcdex(f, g):
    """Compute the extended greatest common divisor of two polynomials.

    Note: This implementation uses PARI, which fails for certain polynomial rings (like
    ZZ), while Sage fails for others. Try comparing both to see which one works better.
    PARI is usually faster when it works correctly.

    References:
        - https://github.com/sagemath/sage/pull/40017
    """
    P = f.parent()
    s, t, r = f._pari_with_name().gcdext(g._pari_with_name())
    s, t, r = P(s), P(t), P(r)
    c = r.leading_coefficient()
    if c != P(0):
        s /= c
        t /= c
        r /= c
    return r, s, t

def resultant(f, g, var):
    """Compute the resultant of two polynomials with respect to `var`.

    Sage currently fails to evaluate `f.resultant(g, var)` over certain rings. As noted
    in [1], the workaround is to find the determinant of the Sylvester matrix.

    References:
        - https://jsur.in/posts/2021-03-07-zer0pts-ctf-2021-crypto-writeups [1]
    """
    return f.sylvester_matrix(g, var).det()
