from hash_framework.utils import print_cmsh

def sha1f(t, b, c, d):
    if 0 <= t <= 19:
        return (b & c) | ((-b) & d)
    elif 20 <= t <= 39:
        return b ^ c ^ d
    elif 40 <= t <= 59:
        return (b & c) | (b & d) | (c & d)
    elif 60 <= t <= 79:
        return b ^ c ^ d
    return 1//0

def sha1k(t):
    if 0 <= t <= 19:
        return 0x5A827999
    elif 20 <= t <= 39:
        return 0x6ED9EBA1
    elif 40 <= t <= 59:
        return 0x8F1BBCDC
    elif 60 <= t <= 79:
        return 0xCA62C1D6
    return 1//0

def sha1_roundfunc(t, state, w):
    a, b, c, d, e = state
    r = a.rotl(5) + sha1f(t, b, c, d) + e + w
    tmp = r + sha1k(t)
    e = d
    d = c
    c = b.rotl(30)
    b = a
    a = tmp
    return a, b, c, d, e

def sha1(model, block, iv=[0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0], rounds=80):
    assert len(block) == 16
    assert len(iv) == 5

    if isinstance(iv[0], int):
        iv = tuple([
            model.to_vector(iv[0], width=32),
            model.to_vector(iv[1], width=32),
            model.to_vector(iv[2], width=32),
            model.to_vector(iv[3], width=32),
            model.to_vector(iv[4], width=32)
        ])

    w = [None] * rounds
    for w_index in range(0, 16):
        if w_index >= len(w):
            break
        if isinstance(block[w_index], int):
            w[w_index] = model.to_vector(block[w_index], width=32)
        else:
            w[w_index] = block[w_index]

    for w_index in range(16, 80):
        if w_index >= len(w):
            break
        w[w_index] = (w[w_index-3] ^ w[w_index - 8] ^ w[w_index - 14] ^ w[w_index - 16]).rotl(1)

    print_cmsh(w)

    state = tuple(iv[:])
    result_rounds = []

    for round_index in range(0, rounds):
        state = sha1_roundfunc(round_index, state, w[round_index])
        result_rounds.append(state)

    result = tuple([
        state[0] + iv[0],
        state[1] + iv[1],
        state[2] + iv[2],
        state[3] + iv[3],
        state[4] + iv[4]
    ])

    return result, result_rounds
