import pytest
from crypy.aes import *


ecb_test_vectors = [
    (
        # 128-bit key
        '7723d87d773a8bbfe1ae5b081235b566',
        '1b0a69b7bc534c16cecffae02cc5323190ceb413f1db3e9f0f79ba654c54b60e',
        'ad5b089515e7821087c61652dc477ab1f2cc6331a70dfc59c9ffb0c723c682f6',
    ),
    (
        # 192-bit key
        'c9c86a51224e5f1916d3f33a602f697afc852a2c44d30d5f',
        '64145e61e61cd96f796b187464fabbde6f42e693f501f1d73b3c606f00801506',
        '502a73e4051cfac8fe6343211a129f5a5f56710c41b32c84da978dda2cec34ad',
    ),
    (
        # 256-bit key
        '7a52e4d342aa07255a7e7c34266cf7302abe2d4dd7ec4468a46187ee61825ffa',
        '7e771c6ee4b26db89050e982ba7e9803c8da34606434dd85d2910e538076d001',
        'a91d8b2ddf37520bc469470ad0dd6394923143ce55386beb1f9c4bd51584658e',
    ),
]
cbc_test_vectors = [
    (
        # 128-bit key
        '0700d603a1c514e46b6191ba430a3a0c',
        'aad1583cd91365e3bb2f0c3430d065bb',
        '068b25c7bfb1f8bdd4cfc908f69dffc5ddc726a197f0e5f720f730393279be91',
        'c4dc61d9725967a3020104a9738f23868527ce839aab1752fd8bdb95a82c4d00',
    ),
    (
        # 192-bit key
        'eab3b19c581aa873e1981c83ab8d83bbf8025111fb2e6b21',
        'f3d6667e8d4d791e60f7505ba383eb05',
        '9d4e4cccd1682321856df069e3f1c6fa391a083a9fb02d59db74c14081b3acc4',
        '51d44779f90d40a80048276c035cb49ca2a47bcb9b9cf7270b9144793787d53f',
    ),
    (
        # 256-bit key
        'dce26c6b4cfb286510da4eecd2cffe6cdf430f33db9b5f77b460679bd49d13ae',
        'fdeaa134c8d7379d457175fd1a57d3fc',
        '50e9eee1ac528009e8cbcd356975881f957254b13f91d7c6662d10312052eb00',
        '2fa0df722a9fd3b64cb18fb2b3db55ff2267422757289413f8f657507412a64c',
    ),
]

@pytest.mark.parametrize('key_hex,pt_hex,ct_hex', ecb_test_vectors)
def test_ecb(key_hex, pt_hex, ct_hex):
    key, pt, ct = map(bytes.fromhex, [key_hex, pt_hex, ct_hex])
    assert ecbenc(pt, key) == ct
    assert ecbdec(ct, key) == pt

@pytest.mark.parametrize('key_hex,iv_hex,pt_hex,ct_hex', cbc_test_vectors)
def test_cbc(key_hex, iv_hex, pt_hex, ct_hex):
    key, iv, pt, ct = map(bytes.fromhex, [key_hex, iv_hex, pt_hex, ct_hex])
    assert cbcenc(pt, key, iv) == ct
    assert cbcdec(ct, key, iv) == pt