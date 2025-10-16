import pytest
from crypy.util import *


def test_b2i():
    assert b2i(b'') == 0
    assert b2i(b'\x00\x00\x04\x02') == 0x402
    assert b2i(b'\x13\x37') == 0x1337

def test_i2b():
    with pytest.raises(ValueError):
        i2b(-1)
    assert i2b(0) == b'\x00'
    assert i2b(0x402) == b'\x04\x02'
    assert i2b(0x1337) == b'\x13\x37'
    assert i2b(0x1337, 4) == b'\x00\x00\x13\x37'

def test_pad():
    assert pad(b'', 16) == b'\x10' * 16
    assert pad(b'a', 16) == b'a' + b'\x0f' * 15
    assert pad(b'abc', 16) == b'abc' + b'\x0d' * 13
    assert pad(b'abcdefg', 16) == b'abcdefg' + b'\x09' * 9
    assert pad(b'x' * 16, 16) == b'x' * 16 + b'\x10' * 16
    assert pad(b'abcd', 8) == b'abcd\x04\x04\x04\x04'
    assert pad(b'abcdefg', 8) == b'abcdefg\x01'

def test_unpad():
    assert unpad(b'\x10' * 16, 16) == b''
    assert unpad(b'a' + b'\x0f' * 15, 16) == b'a'
    assert unpad(b'abc' + b'\x0d' * 13, 16) == b'abc'
    assert unpad(b'abcdefg' + b'\x09' * 9, 16) == b'abcdefg'
    assert unpad(b'x' * 16 + b'\x10' * 16, 16) == b'x' * 16
    assert unpad(b'abcd\x04\x04\x04\x04', 8) == b'abcd'
    assert unpad(b'abcdefg\x01', 8) == b'abcdefg'

def test_zpad():
    assert zpad(b'', 16) == b''
    assert zpad(b'a', 16) == b'a' + b'\x00' * 15
    assert zpad(b'abc', 16) == b'abc' + b'\x00' * 13
    assert zpad(b'abcdefg', 16) == b'abcdefg' + b'\x00' * 9
    assert zpad(b'x' * 16, 16) == b'x' * 16
    assert zpad(b'abcd', 8) == b'abcd\x00\x00\x00\x00'
    assert zpad(b'abcdefg', 8) == b'abcdefg\x00'

@pytest.mark.parametrize('x,word_size,expected', [
    (0, 1, 0),
    (0b1000, 4, 0b0001),
    (0b0101, 4, 0b1010),
    (0b11110000, 4, 0b0000),
    (0b11110001, 4, 0b1000),
    (0b101100, 6, 0b001101),
    (0b10001010, 8, 0b01010001),
    (0b01110111, 8, 0b11101110),
    (0b11111111, 8, 0b11111111),
])
def test_brev(x, word_size, expected):
    assert brev(x, word_size) == expected

@pytest.mark.parametrize('x,word_size,expected', [
    # 4-bit cast
    (0, 4, 0),
    (7, 4, 7),
    (8, 4, -8),
    (15, 4, -1),
    (16, 4, 0),
    # 8-bit cast
    (0, 8, 0),
    (1, 8, 1),
    (-1, 8, -1),
    (127, 8, 127),
    (128, 8, -128),
    (-128, 8, -128),
    (254, 8, -2),
    (255, 8, -1),
    (256, 8, 0),
    # 16-bit cast
    (0x1ffff, 16, -1),
    (-1, 16, -1),
    (-2, 16, -2),
    (-32768, 16, -32768),
    (-32769, 16, 32767),
])
def test_ci(x, word_size, expected):
    assert ci(x, word_size) == expected

@pytest.mark.parametrize('x,word_size,expected', [
    # 4-bit cast
    (0, 4, 0),
    (7, 4, 7),
    (8, 4, 8),
    (15, 4, 15),
    (16, 4, 0),
    # 8-bit cast
    (0, 8, 0),
    (1, 8, 1),
    (-1, 8, 255),
    (127, 8, 127),
    (128, 8, 128),
    (-128, 8, 128),
    (254, 8, 254),
    (255, 8, 255),
    (256, 8, 0),
    # 16-bit cast
    (0x1ffff, 16, 0xffff),
    (-1, 16, 65535),
    (-2, 16, 65534),
    (-32768, 16, 32768),
    (-32769, 16, 32767),
])
def test_cu(x, word_size, expected):
    assert cu(x, word_size) == expected

@pytest.mark.parametrize('x,n,word_size,expected', [
    # 4-bit rotation
    (0b0001, 1, 4, 0b0010),
    (0b0001, 2, 4, 0b0100),
    (0b0001, 3, 4, 0b1000),
    (0b0001, 4, 4, 0b0001),
    (0b1001, 1, 4, 0b0011),
    # 8-bit rotation
    (0b10000000, 1, 8, 0b00000001),
    (0b10000001, 1, 8, 0b00000011),
    (0b11110000, 4, 8, 0b00001111),
    (0xff, 4, 8, 0xff),
    (0b00001111, 8, 8, 0b00001111),
    # 16-bit rotation
    (0x8000, -1, 16, 0x4000),
    (0x8000, 1, 16, 0x0001),
    (0x1234, 4, 16, 0x2341),
    (0xffff, 8, 16, 0xffff),
    (0xabcd, 16, 16, 0xabcd),
    (0x1234, 20, 16, 0x2341),
    # 32-bit rotation
    (0x80000000, 1, 32, 0x00000001),
    (0x00000001, 31, 32, 0x80000000),
])
def test_rol(x, n, word_size, expected):
    assert rol(x, n, word_size) == expected

@pytest.mark.parametrize('x,n,word_size,expected', [
    # 4-bit rotation
    (0b0001, 1, 4, 0b1000),
    (0b0001, 2, 4, 0b0100),
    (0b0001, 3, 4, 0b0010),
    (0b0001, 4, 4, 0b0001),
    (0b1001, 1, 4, 0b1100),
    # 8-bit rotation
    (0b10000000, 1, 8, 0b01000000),
    (0b10000001, 1, 8, 0b11000000),
    (0b11110000, 4, 8, 0b00001111),
    (0xff, 4, 8, 0xff),
    (0b00001111, 8, 8, 0b00001111),
    # 16-bit rotation
    (0x8000, -1, 16, 0x0001),
    (0x8000, 1, 16, 0x4000),
    (0x1234, 4, 16, 0x4123),
    (0xffff, 8, 16, 0xffff),
    (0xabcd, 16, 16, 0xabcd),
    (0x1234, 20, 16, 0x4123),
    # 32-bit rotation
    (0x80000000, 1, 32, 0x40000000),
    (0x00000001, 31, 32, 0x00000002),
])
def test_ror(x, n, word_size, expected):
    assert ror(x, n, word_size) == expected

@pytest.mark.parametrize('s,word_size,endian,signed,expected', [
    (b'\x01', 8, 'little', False, 1),
    (b'\xff', 8, 'little', False, 255),
    (b'\xff', 8, 'little', True, -1),
    (b'\x01\x00', 16, 'little', False, 1),
    (b'\x00\x01', 16, 'big', False, 1),
    (b'\xff\xff', 16, 'little', True, -1),
    (b'\x12\x34', 16, 'big', False, 0x1234),
    (b'\x78\x56\x34\x12', 32, 'little', False, 0x12345678),
    (b'\x12\x34\x56\x78', 32, 'big', False, 0x12345678),
])
def test_unpack(s, word_size, endian, signed, expected):
    assert unpack(s, word_size, endian, signed=signed) == expected

@pytest.mark.parametrize('s,word_size,endian,signed,expected', [
    (b'\x01\x02\x03', 8, 'little', False, [1, 2, 3]),
    (b'\xff\xfe\xfd', 8, 'little', True, [-1, -2, -3]),
    (b'\x01\x00\x02\x00', 16, 'little', False, [1, 2]),
    (b'\x00\x01\x00\x02', 16, 'big', False, [1, 2]),
    (b'\xff\xff\x00\x01', 16, 'little', True, [-1, 256]),
    (b'\x12\x34\x56\x78', 16, 'big', False, [0x1234, 0x5678]),
    (b'\x01\x02\x03\x04\x05', 16, 'little', False, [0x0201, 0x0403, 0x05]),
])
def test_unpacks(s, word_size, endian, signed, expected):
    assert unpacks(s, word_size, endian, signed=signed) == expected

def test_unpack_invalid():
    with pytest.raises(ValueError):
        unpack(b'\x00', 12)
    with pytest.raises(ValueError):
        unpack(b'\x00\x01', 8)
    with pytest.raises(ValueError):
        unpacks(b'\x00', 12)

@pytest.mark.parametrize('s,expected', [
    (b'', ''),
    ('', ''),
    (b'f', 'Zg=='),
    (b'fo', 'Zm8='),
    (b'foo', 'Zm9v'),
    (b'\x00', 'AA=='),
    (b'\xff\xfe\xfd', '//79'),
    (b'\xfa\xfb\xfc\xfd\xfe\xff', '+vv8/f7/'),
])
def test_b64e(s, expected):
    assert b64e(s) == expected

@pytest.mark.parametrize('s,expected', [
    (b'', b''),
    ('', b''),
    ('Zg==', b'f'),
    ('Zm8=', b'fo'),
    ('Zm9v', b'foo'),
    ('AA==', b'\x00'),
    ('AA=', b'\x00'),
    ('AA', b'\x00'),
    ('//79', b'\xff\xfe\xfd'),
    ('+vv8/f7/', b'\xfa\xfb\xfc\xfd\xfe\xff'),
])
def test_b64d(s, expected):
    assert b64d(s) == expected

@pytest.mark.parametrize('s,expected', [
    (b'', ''),
    ('', ''),
    (b'foo', 'Zm9v'),
    (b'\xff\xfe\xfd', '__79'),
    (b'\xfa\xfb\xfc\xfd\xfe\xff', '-vv8_f7_'),
])
def test_b64ue(s, expected):
    assert b64ue(s) == expected

@pytest.mark.parametrize('s,expected', [
    (b'', b''),
    ('', b''),
    ('Zm9v', b'foo'),
    ('__79', b'\xff\xfe\xfd'),
    ('-vv8_f7_', b'\xfa\xfb\xfc\xfd\xfe\xff'),
])
def test_b64ud(s, expected):
    assert b64ud(s) == expected

@pytest.mark.parametrize('args,expected', [
    ((), b''),
    (('a',), b'a'),
    ((b'a',), b'a'),
    ((b'a', b'b'), b'\x03'),
    ((b'xxx', b'xyzz'), b'\x00\x01\x02'),
    ((b'abc', b'xyzabc', b'y'), b'`'),
])
def test_xor(args, expected):
    assert xor(*args) == expected

@pytest.mark.parametrize('args,expected', [
    ((), b''),
    (('a',), b'a'),
    ((b'a',), b'a'),
    ((b'a', b'b'), b'\x03'),
    ((b'xxx', b'xyzz'), b'\x00\x01\x02\x02'),
    ((b'abc', b'xyzabc', b'y'), b'`b`yyy'),
])
def test_xork(args, expected):
    assert xork(*args) == expected
