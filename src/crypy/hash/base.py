from struct import pack, unpack


class HashAlgorithm:
    """Base class for Merkle-Damgård hash functions"""
    block_size = 64
    length_padding_bytes = 8
    endian = 'big'

    @classmethod
    def make_padding(cls, n, offset=0):
        l = (cls.block_size - cls.length_padding_bytes - 1 - n) % cls.block_size
        total_length = 8 * (n + offset)
        length_padding = total_length.to_bytes(cls.length_padding_bytes, cls.endian)
        return b'\x80' + b'\x00' * l + length_padding

    @classmethod
    def pad(cls, data, offset=0):
        return data + cls.make_padding(len(data), offset)

    @classmethod
    def hash(cls, data):
        return cls.compress_blocks(cls.pad(data))

    @classmethod
    def compress_blocks(cls, data, state=None):
        assert len(data) % cls.block_size == 0
        if state is None:
            state = cls.init_state
        for i in range(0, len(data), cls.block_size):
            block = data[i:i+cls.block_size]
            state = cls.compress(block, state)
        return cls.finalize(state)

    @classmethod
    def finalize(cls, state):
        return pack(cls.pack_fmt, *state)

    @classmethod
    def unfinalize(cls, state):
        return unpack(cls.pack_fmt, state)

    @classmethod
    def extend(cls, h, msglen, suffix=b''):
        """Perform a length extension attack.

        Parameters:
            h: The hash digest of the original message.
            msglen: The length of the original message.
            suffix: The suffix of the appended data in the new message.

        Given h = HASH(msg) and the length of the message, this function returns
        (new_h, append), where new_h = HASH(msg || append) and `append` ends with the
        specified `suffix`. More specifically, `append` is the concatenation of the
        generated padding based on `msglen`, and `suffix`.

        Note: Truncated hashes like SHA-224 are susceptible to length extension but
        require substantial amounts of brute force, so they are not implemented here.

        References:
            - https://en.wikipedia.org/wiki/Length_extension_attack
        """
        state = cls.unfinalize(h)
        padding = cls.make_padding(msglen)
        append = padding + suffix
        new_h = cls.compress_blocks(cls.pad(suffix, msglen + len(padding)), state)
        return (new_h, append)