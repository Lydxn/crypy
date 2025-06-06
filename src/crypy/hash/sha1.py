from struct import unpack
from crypy.hash.base import HashAlgorithm
from crypy.util import cu32, rol32


class SHA1(HashAlgorithm):
    """Secure Hash Algorithm 1 (SHA-1), 1995"""
    pack_fmt = '>5I'
    init_state = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0)

    @classmethod
    def compress(cls, data, state):
        W = list(unpack('>16I', data))
        for t in range(16, 80):
            W.append(rol32(W[t - 3] ^ W[t - 8] ^ W[t - 14] ^ W[t - 16], 1))
        A, B, C, D, E = state
        for t in range(80):
            t = rol32(A, 5) + cls._f(t, B, C, D) + E + W[t] + cls._K(t)
            A, B, C, D, E = t & 0xffffffff, A, rol32(B, 30), C, D
        return (
            cu32(state[0] + A),
            cu32(state[1] + B),
            cu32(state[2] + C),
            cu32(state[3] + D),
            cu32(state[4] + E),
        )

    @staticmethod
    def _f(t, B, C, D):
        if 0 <= t <= 19:
            return (B & C) | (~B & D)
        if 20 <= t <= 39 or 60 <= t <= 79:
            return B ^ C ^ D
        if 40 <= t <= 59:
            return (B & C) | (B & D) | (C & D)

    @staticmethod
    def _K(t):
        return (0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6)[t // 20]