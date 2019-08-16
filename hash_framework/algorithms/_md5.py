import cmsh
from .utils import reshape

def md5f(x, y, z):
    return ((y ^ z) & x) ^ z

def md5g(x, y, z):
    return ((x ^ y) & z) ^ y

def md5h(x, y, z):
    return x ^ y ^ z

def md5i(x, y, z):
    return y ^ (x | (-z))

def md5r1(a, b, c, d, x, l, t):
    return b + (md5f(b, c, d) + a + x + t).rotl(l)

def md5r2(a, b, c, d, x, l, t):
    return b + (md5g(b, c, d) + a + x + t).rotl(l)

def md5r3(a, b, c, d, x, l, t):
    return b + (md5h(b, c, d) + a + x + t).rotl(l)

def md5r4(a, b, c, d, x, l, t):
    return b + (md5i(b, c, d) + a + x + t).rotl(l)

def md5_roundfunc(block, round_func, state, x_i, l, t):
    a, b, c, d = state
    new_a = round_func(a, b, c, d, block[x_i], l, t)
    return d, new_a, b, c

def md5(model, block, iv=[0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476], rounds=64):
    block = reshape(model, block, 16, 32)
    iv = reshape(model, iv, 4, 32)

    state = tuple(iv[:])
    result_rounds = []

    shifts = [7, 12, 17, 22]
    xchoice = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    ts = [0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501, 0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821]
    for round_index in range(0, 16):
        if round_index >= rounds:
            break
        state = md5_roundfunc(block, md5r1, state, xchoice[round_index % 16], shifts[round_index % 4], ts[round_index % 16])
        result_rounds.append(state[1])

    shifts = [5, 9, 14, 20]
    xchoice = [1, 6, 11, 0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12]
    ts = [0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8, 0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a]
    for round_index in range(16, 32):
        if round_index >= rounds:
            break
        state = md5_roundfunc(block, md5r2, state, xchoice[round_index % 16], shifts[round_index % 4], ts[round_index % 16])
        result_rounds.append(state[1])

    shifts = [4, 11, 16, 23]
    xchoice = [5, 8, 11, 14, 1, 4, 7, 10, 13, 0, 3, 6, 9, 12, 15, 2]
    ts = [0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70, 0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665]
    for round_index in range(32, 48):
        if round_index >= rounds:
            break
        state = md5_roundfunc(block, md5r3, state, xchoice[round_index % 16], shifts[round_index % 4], ts[round_index % 16])
        result_rounds.append(state[1])

    shifts = [6, 10, 15, 21]
    xchoice = [0, 7, 14, 5, 12, 3, 10, 1, 8, 15, 6, 13, 4, 11, 2, 9]
    ts = [0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1, 0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391]
    for round_index in range(48, 64):
        if round_index >= rounds:
            break
        state = md5_roundfunc(block, md5r4, state, xchoice[round_index % 16], shifts[round_index % 4], ts[round_index % 16])
        result_rounds.append(state[1])

    result = tuple([
        state[0] + iv[0],
        state[1] + iv[1],
        state[2] + iv[2],
        state[3] + iv[3]
    ])

    return result, result_rounds
