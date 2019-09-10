import cmsh
from .utils import reshape


def md4f(x, y, z):
    return (x & y) | ((-x) & z)


def md4g(x, y, z):
    return (x & y) | (x & z) | (y & z)


def md4h(x, y, z):
    return x ^ y ^ z


def md4r1(a, b, c, d, x, l):
    return (a + md4f(b, c, d) + x).rotl(l)


def md4r2(a, b, c, d, x, l):
    return ((a + md4g(b, c, d) + x) + 0x5A827999).rotl(l)


def md4r3(a, b, c, d, x, l):
    return ((a + md4h(b, c, d) + x) + 0x6ED9EBA1).rotl(l)


def md4_round(block, round_func, state, x_i, l):
    a, b, c, d = state
    new_a = round_func(a, b, c, d, block[x_i], l)
    return d, new_a, b, c


def md4(model, block, iv=[0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476], rounds=48):
    block = reshape(model, block, 16, 32)
    iv = reshape(model, iv, 4, 32)

    state = tuple(iv[:])
    result_rounds = []

    shifts = [3, 7, 11, 19]
    xchoice = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for round_index in range(0, 16):
        if round_index >= rounds:
            break
        state = md4_round(
            block, md4r1, state, xchoice[round_index % 16], shifts[round_index % 4]
        )
        result_rounds.append(state[1])

    shifts = [3, 5, 9, 13]
    xchoice = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
    for round_index in range(16, 32):
        if round_index >= rounds:
            break
        state = md4_round(
            block, md4r2, state, xchoice[round_index % 16], shifts[round_index % 4]
        )
        result_rounds.append(state[1])

    shifts = [3, 9, 11, 15]
    xchoice = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]
    for round_index in range(32, 48):
        if round_index >= rounds:
            break
        state = md4_round(
            block, md4r3, state, xchoice[round_index % 16], shifts[round_index % 4]
        )
        result_rounds.append(state[1])

    result = tuple(
        [state[0] + iv[0], state[1] + iv[1], state[2] + iv[2], state[3] + iv[3]]
    )
    return result, result_rounds
