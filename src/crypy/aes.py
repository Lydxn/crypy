from Crypto.Cipher import AES

__all__ = [
    'cbcdec',
    'cbcenc',
    'ecbdec',
    'ecbenc',
]

def ecbenc(pt, key):
    """Encrypt a 16-byte aligned plaintext with AES-ECB."""
    return AES.new(key, AES.MODE_ECB).encrypt(pt)

def ecbdec(ct, key):
    """Decrypt a 16-byte aligned ciphertext with AES-ECB."""
    return AES.new(key, AES.MODE_ECB).decrypt(ct)

def cbcenc(pt, key, iv):
    """Encrypt a 16-byte aligned plaintext with AES-CBC."""
    return AES.new(key, AES.MODE_CBC, iv).encrypt(pt)

def cbcdec(ct, key, iv):
    """Decrypt a 16-byte aligned ciphertext with AES-CBC."""
    return AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
