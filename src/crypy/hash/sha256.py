from struct import unpack
from crypy.hash.base import HashAlgorithm
from crypy.util import cu32, ror32


class SHA256(HashAlgorithm):
    """Secure Hash Algorithm 2 (SHA-256), 2001"""
    pack_fmt = '>8I'
    init_state = (
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    )

    K = (
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
        0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
        0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
	    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
        0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    )

    @classmethod
    def compress(cls, data, state):
        W = list(unpack('>16I', data))
        for t in range(16, 64):
            w = cls.SSIG1(W[t - 2]) + W[t - 7] + cls.SSIG0(W[t - 15]) + W[t - 16]
            W.append(cu32(w))
        a, b, c, d, e, f, g, h = state
        for t in range(64):
            T1 = cu32(h + cls.BSIG1(e) + cls.CH(e, f, g) + cls.K[t] + W[t])
            T2 = cu32(cls.BSIG0(a) + cls.MAJ(a, b, c))
            a, b, c, d, e, f, g, h = cu32(T1 + T2), a, b, c, cu32(d + T1), e, f, g
        return (
            cu32(state[0] + a),
            cu32(state[1] + b),
            cu32(state[2] + c),
            cu32(state[3] + d),
            cu32(state[4] + e),
            cu32(state[5] + f),
            cu32(state[6] + g),
            cu32(state[7] + h),
        )

    @staticmethod
    def CH(x, y, z):
        return (x & y) ^ (~x & z)

    @staticmethod
    def MAJ(x, y, z):
        return (x & y) ^ (x & z) ^ (y & z)

    @staticmethod
    def BSIG0(x):
        return ror32(x, 2) ^ ror32(x, 13) ^ ror32(x, 22)

    @staticmethod
    def BSIG1(x):
        return ror32(x, 6) ^ ror32(x, 11) ^ ror32(x, 25)

    @staticmethod
    def SSIG0(x):
        return ror32(x, 7) ^ ror32(x, 18) ^ (x >> 3)

    @staticmethod
    def SSIG1(x):
        return ror32(x, 17) ^ ror32(x, 19) ^ (x >> 10)


class SHA224(SHA256):
    """Secure Hash Algorithm 2 (SHA-224), 2001"""
    pack_fmt = '>7I'
    init_state = (
        0xc1059ed8, 0x367cd507, 0x3070dd17, 0xf70e5939,
        0xffc00b31, 0x68581511, 0x64f98fa7, 0xbefa4fa4,
    )

    @classmethod
    def finalize(cls, state):
        return super().finalize(state[:7])

    @classmethod
    def unfinalize(cls, state):
        return super().unfinalize(state) + (None,)