from crypy.util import b2i, brev, i2b, zpad

__all__ = [
    'b2gcm',
    'gcm2b',
    'gcm2i',
    'gcm_unpack',
    'gfield',
    'gobj',
    'i2gcm',
]


_gcm_obj = None
_gcm_field = None

def gfield():
    """Generate the AES-GCM field GF(2^128)."""
    from sage.all import GF

    global _gcm_field
    if _gcm_field is None:
        x = GF(2).polynomial_ring().gen()
        _gcm_field = GF(2**128, 'x', modulus=x**128 + x**7 + x**2 + x + 1)
    return _gcm_field

def gobj():
    """Generate the PolynomialRing object over gfield()."""
    from sage.all import PolynomialRing

    global _gcm_obj
    if _gcm_obj is None:
        _gcm_obj = PolynomialRing(gfield(), 'x').objgen()
    return _gcm_obj

def b2gcm(b):
    """Convert a byte string to an element of the AES-GCM field."""
    return l2gcm(b2l(b))

def gcm2b(g):
    """Convert an element of the AES-GCM field to a byte string."""
    return l2b(gcm2l(g))

def i2gcm(n):
    """Convert a 128-bit integer to an element of the AES-GCM field."""
    return gfield().from_integer(brev(n, 128))

def gcm2i(g):
    """Convert an element of the AES-GCM field to a 128-bit integer."""
    return brev(g.to_integer(), 128)

def gcm_unpack(ct):
    """Unpack a ciphertext into 16-byte blocks in the AES-GCM field.

    Note: the ciphertext is zero-padded if it's not a multiple of 16.
    """
    ct = zpad(ct, 16)
    return [b2gcm(ct[i:i+16]) for i in range(0, len(ct), 16)]
