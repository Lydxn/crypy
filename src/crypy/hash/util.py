from Crypto.Hash import MD2, MD4
import hashlib

__all__ = [
    'md2',
    'md4',
    'md5',
    'sha1',
    'sha224',
    'sha256',
    'sha384',
    'sha512',
]


def md2(s):
    """Compute the MD2 hash of a message."""
    return MD2.new(s).digest()

def md4(s):
    """Compute the MD4 hash of a message."""
    return MD4.new(s).digest()

def md5(s):
    """Compute the MD5 hash of a message."""
    return hashlib.md5(s).digest()

def sha1(s):
    """Compute the SHA-1 hash of a message."""
    return hashlib.sha1(s).digest()

def sha224(s):
    """Compute the SHA-224 hash of a message."""
    return hashlib.sha224(s).digest()

def sha256(s):
    """Compute the SHA-256 hash of a message."""
    return hashlib.sha256(s).digest()

def sha384(s):
    """Compute the SHA-384 hash of a message."""
    return hashlib.sha384(s).digest()

def sha512(s):
    """Compute the SHA-512 hash of a message."""
    return hashlib.sha512(s).digest()