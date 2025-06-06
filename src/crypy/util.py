from Crypto.Util.number import bytes_to_long, long_to_bytes

__all__ = [
    'b2l',
    'l2b',
    'ci',
    'ci8',
    'ci16',
    'ci32',
    'ci64',
    'cu',
    'cu8',
    'cu16',
    'cu32',
    'cu64',
    'rol',
    'rol8',
    'rol16',
    'rol32',
    'rol64',
    'ror',
    'ror8',
    'ror16',
    'ror32',
    'ror64',
]


def b2l(b):
    """Alias of `Crypto.Util.number.bytes_to_long`.

    Convert a byte string to a long integer (big endian).
    """
    return bytes_to_long(b)

def l2b(l):
    """Alias of `Crypto.Util.number.long_to_bytes`.

    Convert a positive integer to a byte string (big endian).
    """
    return long_to_bytes(l)

def ci(x, word_size):
    """Cast `x` to an signed integer of `word_size` bits."""
    x &= ((1 << word_size) - 1)
    return x - (1 << word_size) if x & (1 << (word_size - 1)) else x

def cu(x, word_size):
    """Cast `x` to an unsigned integer of `word_size` bits."""
    return x & ((1 << word_size) - 1)

def rol(x, n, word_size):
    """Rotate `x` to the left by `n` bits"""
    mask = (1 << word_size) - 1
    n %= word_size
    x &= mask
    return (x << n | x >> (word_size - n)) & mask

def ror(x, n, word_size):
    """Rotate `x` to the right by `n` bits"""
    mask = (1 << word_size) - 1
    n %= word_size
    x &= mask
    return (x >> n | x << (word_size - n)) & mask

# These are 8-, 16-, 32- and 64-bit versions of some routines
ci8 = lambda x: ci(x, 8)
ci16 = lambda x: ci(x, 16)
ci32 = lambda x: ci(x, 32)
ci64 = lambda x: ci(x, 64)
cu8 = lambda x: cu(x, 8)
cu16 = lambda x: cu(x, 16)
cu32 = lambda x: cu(x, 32)
cu64 = lambda x: cu(x, 64)
rol8 = lambda x, n: rol(x, n, 8)
rol16 = lambda x, n: rol(x, n, 16)
rol32 = lambda x, n: rol(x, n, 32)
rol64 = lambda x, n: rol(x, n, 64)
ror8 = lambda x, n: ror(x, n, 8)
ror16 = lambda x, n: ror(x, n, 16)
ror32 = lambda x, n: ror(x, n, 32)
ror64 = lambda x, n: ror(x, n, 64)