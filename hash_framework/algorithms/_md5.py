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


def md5(model, block, iv=[0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476], rounds=64):
    block = reshape(model, block, 16, 32)
    iv = reshape(model, iv, 4, 32)

    state = tuple(iv[:])
    result_rounds = []

    shifts = [7, 12, 17, 22]
    xchoice = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    ts = [
        0xD76AA478,
        0xE8C7B756,
        0x242070DB,
        0xC1BDCEEE,
        0xF57C0FAF,
        0x4787C62A,
        0xA8304613,
        0xFD469501,
        0x698098D8,
        0x8B44F7AF,
        0xFFFF5BB1,
        0x895CD7BE,
        0x6B901122,
        0xFD987193,
        0xA679438E,
        0x49B40821,
    ]
    for round_index in range(0, 16):
        if round_index >= rounds:
            break
        state = md5_roundfunc(
            block,
            md5r1,
            state,
            xchoice[round_index % 16],
            shifts[round_index % 4],
            ts[round_index % 16],
        )
        result_rounds.append(state[1])

    shifts = [5, 9, 14, 20]
    xchoice = [1, 6, 11, 0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12]
    ts = [
        0xF61E2562,
        0xC040B340,
        0x265E5A51,
        0xE9B6C7AA,
        0xD62F105D,
        0x02441453,
        0xD8A1E681,
        0xE7D3FBC8,
        0x21E1CDE6,
        0xC33707D6,
        0xF4D50D87,
        0x455A14ED,
        0xA9E3E905,
        0xFCEFA3F8,
        0x676F02D9,
        0x8D2A4C8A,
    ]
    for round_index in range(16, 32):
        if round_index >= rounds:
            break
        state = md5_roundfunc(
            block,
            md5r2,
            state,
            xchoice[round_index % 16],
            shifts[round_index % 4],
            ts[round_index % 16],
        )
        result_rounds.append(state[1])

    shifts = [4, 11, 16, 23]
    xchoice = [5, 8, 11, 14, 1, 4, 7, 10, 13, 0, 3, 6, 9, 12, 15, 2]
    ts = [
        0xFFFA3942,
        0x8771F681,
        0x6D9D6122,
        0xFDE5380C,
        0xA4BEEA44,
        0x4BDECFA9,
        0xF6BB4B60,
        0xBEBFBC70,
        0x289B7EC6,
        0xEAA127FA,
        0xD4EF3085,
        0x04881D05,
        0xD9D4D039,
        0xE6DB99E5,
        0x1FA27CF8,
        0xC4AC5665,
    ]
    for round_index in range(32, 48):
        if round_index >= rounds:
            break
        state = md5_roundfunc(
            block,
            md5r3,
            state,
            xchoice[round_index % 16],
            shifts[round_index % 4],
            ts[round_index % 16],
        )
        result_rounds.append(state[1])

    shifts = [6, 10, 15, 21]
    xchoice = [0, 7, 14, 5, 12, 3, 10, 1, 8, 15, 6, 13, 4, 11, 2, 9]
    ts = [
        0xF4292244,
        0x432AFF97,
        0xAB9423A7,
        0xFC93A039,
        0x655B59C3,
        0x8F0CCC92,
        0xFFEFF47D,
        0x85845DD1,
        0x6FA87E4F,
        0xFE2CE6E0,
        0xA3014314,
        0x4E0811A1,
        0xF7537E82,
        0xBD3AF235,
        0x2AD7D2BB,
        0xEB86D391,
    ]
    for round_index in range(48, 64):
        if round_index >= rounds:
            break
        state = md5_roundfunc(
            block,
            md5r4,
            state,
            xchoice[round_index % 16],
            shifts[round_index % 4],
            ts[round_index % 16],
        )
        result_rounds.append(state[1])

    result = tuple(
        [state[0] + iv[0], state[1] + iv[1], state[2] + iv[2], state[3] + iv[3]]
    )

    return result, result_rounds
