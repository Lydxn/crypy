from random import randrange
import os
import pytest
from crypy.hash import *

@pytest.mark.parametrize('hasher,hashfunc', [
    (MD4, md4),
    (MD5, md5),
    (SHA1, sha1),
    (SHA224, sha224),
    (SHA256, sha256),
    (SHA384, sha384),
    (SHA512, sha512),
])
def test_hashers(hasher, hashfunc):
    for n in range(hasher.block_size * 2 + 2):
        data = os.urandom(n)
        assert hasher.hash(data) == hashfunc(data)

def test_util_hashes():
    s = b'The quick brown fox jumps over the lazy dog'
    assert md2(s).hex() == '03d85a0d629d2c442e987525319fc471'
    assert md4(s).hex() == '1bee69a46ba811185c194762abaeae90'
    assert md5(s).hex() == '9e107d9d372bb6826bd81d3542a419d6'
    assert sha1(s).hex() == '2fd4e1c67a2d28fced849ee1bb76e7391b93eb12'
    assert sha224(s).hex() == '730e109bd7a8a32b1cb9d9a09aa2325d2430587ddbc0c38bad911525'
    assert sha256(s).hex() == 'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592'
    assert sha384(s).hex() == (
        'ca737f1014a48f4c0b6dd43cb177b0afd9e5169367544c49'
        '4011e3317dbf9a509cb1e5dc1e85a941bbee3d7f2afbc9b1'
    )
    assert sha512(s).hex() == (
        '07e547d9586f6a73f73fbac0435ed76951218fb7d0c8d788a309d785436bbb64'
        '2e93a252a954f23912547d1e8a3b5ed6e1bfd7097821233fa0538f3db854fee6'
    )

@pytest.mark.parametrize('hasher,hashfunc', [
    (MD4, md4),
    (MD5, md5),
    (SHA1, sha1),
    (SHA256, sha256),
    (SHA512, sha512),
])
def test_extend(hasher, hashfunc):
    for n in range(hasher.block_size * 2 + 2):
        data = os.urandom(n)
        suffix = os.urandom(randrange(n + 1, (n + 1) * 3))
        h = hashfunc(data)
        new_h, append = hasher.extend(h, len(data), suffix)
        assert hashfunc(data + append) == new_h