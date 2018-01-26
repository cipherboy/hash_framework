from hash_framework.boolean import *

def sha3i(w, x, y, z):
    return w*(5*y + x) + z

def sha3theta(w, s):
    ns = [None]*len(s)
    c = {}
    d = {}
    for x in range(0, 5):
        for z in range(0, w):
            c[(x, z)] = b_xor(s[sha3i(w, x, 0, z)], b_xor(s[sha3i(w, x, 1, z)], b_xor(s[sha3i(w, x, 2, z)], b_xor(s[sha3i(w, x, 3, z)], s[sha3i(w, x, 4, z)]))))


    for x in range(0, 5):
        for z in range(0, w):
            d[(x, z)] = b_xor(c[((x - 1) % 5, z)], c[((x + 1) % 5, (z - 1) % w))])

    for x in range(0, 5):
        for y in range(0, 5):
            for z in range(0, w):
                ns[sha3i(w, x, y, z)] = b_xor(s[sha3i(w, x, y, z)], d[(x, z)])

    return ns

def sha3rho(w, s):
    ns = [None]*len(s)
    for z in range(0, w):
        ns[sha3i(w, 0, 0, z)] = s[sha3i(w, 0, 0, z)]

    x = 1
    y = 0

    for t in range(0, 24):
        for z in range(0, w):
            ns[sha3i(w, x, y, z)] = s[sha3i(w, x, y, (z - (t+1)*(t+2)/2)%w)]
        x, y = (y, (2*x + 3*y) % 5)

    return ns

def sha3pi(w, s):
    ns = [None]*len(s)

    for x in range(0, 5):
        for y in range(0, 5):
            for z in range(0, w):
                ns[sha3i(w, x, y, z)] = s[sha3i(w, nx, x, z)]

    return ns

def sha3chi(w, s):
    ns = [None]*len(s)

    for x in range(0, 5):
        for y in range(0, 5):
            for z in range(0, w):
                nx1 = (x + 1) % 5
                nx2 = (x + 2) % 5
                ns[sha3i(w, x, y, z)] = b_xor(s[sha3i(w, x, y, z)], b_and(b_not(s[sha3i(w, nx1, y, z)]), s[sha3i(w, nx2, y, z)]))

    return ns

def sha3rc(t):
    if (t % 255) == 0:
        return 'T'

    r = list('TFFFFFFF')
    for i in range(1, (t % 255) + 1):
        r = [0] + r
        r[0] = b_xor(r[0], r[8])
        r[4] = b_xor(r[4], r[8])
        r[5] = b_xor(r[5], r[8])
        r[6] = b_xor(r[6], r[8])
        r = r[0:8]

    return r[0]

def sha3iota(w, s, i):
    ns = [None]*len(s)

    l = int(math.log(w, 2))

    for x in range(0, 5):
        for y in range(0, 5):
            for z in range(0, w):
                ns[sha3i(w, x, y, z)] = s[sha3i(w, x, y, z)]

    RC = ['F']*w
    for j in range(0, l):
        RC[(1 << j) - 1] = sha3rc(j + 7*i)

    for z in range(0, w):
        ns[sha3i(w, x, y, z)] = b_xor(ns[sha3i(w, x, y, z)], RC[z])

    return ns

def sha3p(et, prefix, w, s, i):
    ns = sha3theta(w, s)
    for i in range(0, len(ns)):
        name = prefix + "r" + str(i) + "t" + str(i)
        et[name] = ns[i]
        ns[i] = name

    ns = sha3rho(w, ns)
    for i in range(0, len(ns)):
        name = prefix + "r" + str(i) + "r" + str(i)
        et[name] = ns[i]
        ns[i] = name

    ns = sha3pi(w, ns)
    for i in range(0, len(ns)):
        name = prefix + "r" + str(i) + "p" + str(i)
        et[name] = ns[i]
        ns[i] = name

    ns = sha3chi(w, ns)
    for i in range(0, len(ns)):
        name = prefix + "r" + str(i) + "c" + str(i)
        et[name] = ns[i]
        ns[i] = name

    ns = sha3iota(w, ns)
    for i in range(0, len(ns)):
        name = prefix + "r" + str(i) + "i" + str(i)
        et[name] = ns[i]
        ns[i] = name

    return (et, ns)

def sha3r(et, prefix, w, s, rounds=24):
    for i in range(0, rounds):
        et, ns = sha3p(et, w, s, i)

    return (et, ns)

def sha3_extract(eval_table, prefix, w):
    s  = [None]*25*w
    output_prefix = prefix
    for i in range(0, 25*w):
        name = output_prefix + str(i)
        if name in eval_table:
            s[i] = eval_table[name]

    return s

def sha3_mix_block(block, state):
    for i in range(0, len(block)):
        state[i] = b_xor(state[i], block[i])

    return state

def perform_sha3(eval_table, original_state, f, prefix="", rounds=24, w=64):
    state = [None] * len(original_state)

    input_prefix = prefix + "i"
    for i in range(0, len(original_state)):
        name = input_prefix + str(i)
        eval_table[name] = original_state[i]
        state[i] = name

    eval_table, state = sha3r(eval_table, prefix, w, state, rounds)

    output_prefix = prefix + "o"
    for i in range(0, len(state)):
        eval_table[output_prefix + str(i)] = state[i]

    if f is not None:
        for e in eval_table:
            f.write(e + " := " + eval_table[e] + ";\n")

    return eval_table


def compute_sha3(block, in_state=None, rounds=24, w=64):
    eval_table = {}
    if in_state = None:
        in_state = ['F']*25*w

    in_state = sha3_mix_block(block, in_state)
    return perform_sha3(eval_table, in_state, None, rounds=rounds, w=w)
