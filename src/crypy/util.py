from Crypto.Util.Padding import pad as _pad, unpad as _unpad
from Crypto.Util.number import bytes_to_long, long_to_bytes
import base64

__all__ = [
    'b2l',
    'b64d',
    'b64e',
    'b64ud',
    'b64ue',
    'brev',
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
    'pad',
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
    'unpad',
    'xor',
    'xork',
    'zpad',
]


def b2l(b):
    """Alias of `Crypto.Util.number.bytes_to_long`.

    Convert a byte string to a long integer (big endian).
    """
    return bytes_to_long(b)

def l2b(l, blocksize=0):
    """Alias of `Crypto.Util.number.long_to_bytes`.

    Convert a positive integer to a byte string (big endian).
    """
    return long_to_bytes(l, blocksize)

def pad(data, block_size):
    """Alias of `Crypto.Util.Padding.pad`.

    Apply PKCS #7 padding to a byte string up to a multiple of `block_size`.
    """
    return _pad(data, block_size)

def unpad(data, block_size):
    """Alias of `Crypto.Util.Padding.unpad`.

    Remove PKCS #7 padding from a byte string. The input length must be a multiple of
    `block_size`.
    """
    return _unpad(data, block_size)

def zpad(data, block_size):
    """Pad a byte string with null bytes to the next multiple of `block_size`."""
    return data + b'\x00' * (-len(data) % block_size)

def brev(x, word_size):
    """Compute the bit reversal of an integer `x` with `word_size` bits."""
    x &= ((1 << word_size) - 1)
    return int(f'{x:0{word_size}b}'[::-1], 2)

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

def b64e(s):
    """Encode a string in Base64."""
    if isinstance(s, str):
        s = s.encode()
    return base64.b64encode(s).decode()

def b64d(s):
    """Decode a string in Base64."""
    if isinstance(s, str):
        s = s.encode()
    return base64.b64decode(s + b'==')

def b64ue(s):
    """Encode a string in Base64Url."""
    if isinstance(s, str):
        s = s.encode()
    return base64.urlsafe_b64encode(s).decode()

def b64ud(s):
    """Decode a string in Base64Url."""
    if isinstance(s, str):
        s = s.encode()
    return base64.urlsafe_b64decode(s + b'==')

def xor(*args):
    """XOR multiple string or byte inputs, truncated to the length of the shortest string.

    Analagous to pwntools' xor(..., cut='min').
    """
    return _xor_generic(args, lambda strs: min(len(s) for s in strs))

def xork(*args):
    """XOR multiple string or byte inputs cyclically.

    Analagous to pwntools' xor(..., cut='max').
    """
    return _xor_generic(args, lambda strs: max(len(s) for s in strs))

def _xor_generic(args, cut_func):
    """XOR multiple string or byte inputs.

    The function takes any number of string or bytes-like arguments. Each string is
    cyclically padded to the length returned by `cut_func`.
    """
    if not args:
        return b''
    strs = []
    for s in args:
        if isinstance(s, str):
            s = s.encode()
        strs.append(bytes(s))
    n = cut_func(strs)
    xored = bytearray(n)
    for s in strs:
        j, m = 0, len(s)
        for i in range(n):
            xored[i] ^= s[j]
            j += 1
            if j == m:
                j = 0
    return bytes(xored)