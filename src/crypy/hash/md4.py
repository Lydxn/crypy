from struct import unpack
from crypy.hash.base import HashAlgorithm
from crypy.util import rol32, cu32


class MD4(HashAlgorithm):
    """Message-Digest Algorithm (MD4), 1990"""
    endian = 'little'
    pack_fmt = '<4I'
    init_state = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476)

    S = (
        3, 7, 11, 19, 3, 7, 11, 19, 3, 7, 11, 19, 3, 7, 11, 19,
        3, 5, 9, 13, 3, 5, 9, 13, 3, 5, 9, 13, 3, 5, 9, 13,
        3, 9, 11, 15, 3, 9, 11, 15, 3, 9, 11, 15, 3, 9, 11, 15,
    )
    J = (
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
        0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15,
        0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15,
    )

    @classmethod
    def compress(cls, data, state):
        X = unpack('<16I', data)
        A, B, C, D = state
        for i in range(48):
            match i // 16:
                case 0:
                    E = cls.F(B, C, D)
                case 1:
                    E = cls.G(B, C, D) + 0x5A827999
                case 2:
                    E = cls.H(B, C, D) + 0x6ED9EBA1
            t = rol32(A + E + X[cls.J[i]], cls.S[i])
            A, B, C, D = D, t, B, C
        return (
            cu32(state[0] + A),
            cu32(state[1] + B),
            cu32(state[2] + C),
            cu32(state[3] + D),
        )

    @staticmethod
    def F(x, y, z):
        return (x & y) | (~x & z)

    @staticmethod
    def G(x, y, z):
        return (x & y) | (x & z) | (y & z)

    @staticmethod
    def H(x, y, z):
        return x ^ y ^ z