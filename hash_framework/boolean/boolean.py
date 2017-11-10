#!/usr/bin/python

from hash_simplify import *
from hash_translate import *

def hash_and(x, y):
    return simplify(('and', x, y))

def hash_or(x, y):
    return simplify(('or', x, y))

def hash_not(x):
    return simplify(('not', x))

def hash_xor(x, y):
    #return simplify(hash_or(hash_and(x, hash_not(y)), hash_and(hash_not(x), y)))
    return simplify(('xor', x, y))

def hash_fac(x, y, c):
    return simplify(hash_or(hash_and(x, y), hash_and(c, hash_or(x, y))))

def hash_fav(x, y, c):
    return simplify(hash_xor(hash_xor(x, y), c))

def hash_andbit(b, x):
    r = []
    return r

def hash_addl(x, y):
    c = "F"
    r = []
    assert(len(x) == len(y)) # Assert fixed-sized numbers
    for i in range(len(x) - 1, -1, -1):
        r.append(simplify(hash_fav(x[i], y[i], c)))
        c = simplify(hash_fac(x[i], y[i], c))
    r.reverse()
    return r

def hash_fav4(c0, c1, x1, x2, x3, x4):
    return simplify(('xor', c0, c1, x1, x2, x3, x4))

def hash_fac4(c0, c1, x1, x2, x3, x4):
    return simplify(('or', ('and', ('not', x1), ('not', x2), ('not', x3), ('not', x4), c0, c1), ('and', ('not', x1), ('not', x2), ('not', x3), x4, ('not', c0), c1), ('and', ('not', x1), ('not', x2), ('not', x3), x4, c0, ('not', c1)), ('and', ('not', x1), ('not', x2), ('not', x3), x4, c0, c1), ('and', ('not', x1), ('not', x2), x3, ('not', x4), ('not', c0), c1), ('and', ('not', x1), ('not', x2), x3, ('not', x4), c0, ('not', c1)), ('and', ('not', x1), ('not', x2), x3, ('not', x4), c0, c1), ('and', ('not', x1), ('not', x2), x3, x4, ('not', c0), ('not', c1)), ('and', ('not', x1), ('not', x2), x3, x4, ('not', c0), c1), ('and', ('not', x1), ('not', x2), x3, x4, c0, ('not', c1)), ('and', ('not', x1), x2, ('not', x3), ('not', x4), ('not', c0), c1), ('and', ('not', x1), x2, ('not', x3), ('not', x4), c0, ('not', c1)), ('and', ('not', x1), x2, ('not', x3), ('not', x4), c0, c1), ('and', ('not', x1), x2, ('not', x3), x4, ('not', c0), ('not', c1)), ('and', ('not', x1), x2, ('not', x3), x4, ('not', c0), c1), ('and', ('not', x1), x2, ('not', x3), x4, c0, ('not', c1)), ('and', ('not', x1), x2, x3, ('not', x4), ('not', c0), ('not', c1)), ('and', ('not', x1), x2, x3, ('not', x4), ('not', c0), c1), ('and', ('not', x1), x2, x3, ('not', x4), c0, ('not', c1)), ('and', ('not', x1), x2, x3, x4, ('not', c0), ('not', c1)), ('and', x1, ('not', x2), ('not', x3), ('not', x4), ('not', c0), c1), ('and', x1, ('not', x2), ('not', x3), ('not', x4), c0, ('not', c1)), ('and', x1, ('not', x2), ('not', x3), ('not', x4), c0, c1), ('and', x1, ('not', x2), ('not', x3), x4, ('not', c0), ('not', c1)), ('and', x1, ('not', x2), ('not', x3), x4, ('not', c0), c1), ('and', x1, ('not', x2), ('not', x3), x4, c0, ('not', c1)), ('and', x1, ('not', x2), x3, ('not', x4), ('not', c0), ('not', c1)), ('and', x1, ('not', x2), x3, ('not', x4), ('not', c0), c1), ('and', x1, ('not', x2), x3, ('not', x4), c0, ('not', c1)), ('and', x1, ('not', x2), x3, x4, ('not', c0), ('not', c1)), ('and', x1, x2, ('not', x3), ('not', x4), ('not', c0), ('not', c1)), ('and', x1, x2, ('not', x3), ('not', x4), ('not', c0), c1), ('and', x1, x2, ('not', x3), ('not', x4), c0, ('not', c1)), ('and', x1, x2, ('not', x3), x4, ('not', c0), ('not', c1)), ('and', x1, x2, x3, ('not', x4), ('not', c0), ('not', c1)), ('and', x1, x2, x3, x4, c0, c1)))

def hash_facc4(c0, c1, x1, x2, x3, x4):
    return simplify(('or', ('and', ('not', x1), ('not', x2), x3, x4, c0, c1), ('and', ('not', x1), x2, ('not', x3), x4, c0, c1), ('and', ('not', x1), x2, x3, ('not', x4), c0, c1), ('and', ('not', x1), x2, x3, x4, ('not', c0), c1), ('and', ('not', x1), x2, x3, x4, c0, ('not', c1)), ('and', ('not', x1), x2, x3, x4, c0, c1), ('and', x1, ('not', x2), ('not', x3), x4, c0, c1), ('and', x1, ('not', x2), x3, ('not', x4), c0, c1), ('and', x1, ('not', x2), x3, x4, ('not', c0), c1), ('and', x1, ('not', x2), x3, x4, c0, ('not', c1)), ('and', x1, ('not', x2), x3, x4, c0, c1), ('and', x1, x2, ('not', x3), ('not', x4), c0, c1), ('and', x1, x2, ('not', x3), x4, ('not', c0), c1), ('and', x1, x2, ('not', x3), x4, c0, ('not', c1)), ('and', x1, x2, ('not', x3), x4, c0, c1), ('and', x1, x2, x3, ('not', x4), ('not', c0), c1), ('and', x1, x2, x3, ('not', x4), c0, ('not', c1)), ('and', x1, x2, x3, ('not', x4), c0, c1), ('and', x1, x2, x3, x4, ('not', c0), ('not', c1)), ('and', x1, x2, x3, x4, ('not', c0), c1), ('and', x1, x2, x3, x4, c0, ('not', c1)), ('and', x1, x2, x3, x4, c0, c1)))

def hash_add4l(eval_table, prefix, x1, x2, x3, x4):
    assert(len(x1) == len(x2))
    assert(len(x1) == len(x3))
    assert(len(x1) == len(x4))

    for i in range(0, len(x1)):
        if type(x1[i]) == type((1, 2)):
            var = clause_dedupe(simplify(x1[i]), prefix)
            x1[i] = var
        if type(x2[i]) == type((1, 2)):
            var = clause_dedupe(simplify(x2[i]), prefix)
            x2[i] = var
        if type(x3[i]) == type((1, 2)):
            var = clause_dedupe(simplify(x3[i]), prefix)
            x3[i] = var
        if type(x4[i]) == type((1, 2)):
            var = clause_dedupe(simplify(x4[i]), prefix)
            x4[i] = var

    r = []
    c0 = ["F"]*len(x1)
    c1 = ["F"]*len(x1)
    for i in range(len(x1) - 1, -1, -1):
        r.append(hash_fav4(c0[i], c1[i], x1[i], x2[i], x3[i], x4[i]))
        nc0 = hash_fac4(c0[i], c1[i], x1[i], x2[i], x3[i], x4[i])
        nc1 = hash_facc4(c0[i], c1[i], x1[i], x2[i], x3[i], x4[i])
        if type(nc0) == type((1, 2)):
            var = clause_dedupe(simplify(nc0), prefix)
            nc0 = var
        if type(nc1) == type((1, 2)):
            var = clause_dedupe(simplify(nc1), prefix)
            nc1 = var
        c0[i-1] = nc0
        c1[i-2] = nc1
    r.reverse()
    return r, eval_table

def hash_mul(a, b):
    assert(len(a) == len(b))
    adds = []
    for i in range(0, len(b)):
        pass

def hash_rotl(x, l):
    return x[l:] + x[:l]

def hash_tobitl(num):
    r = []
    for i in range(31, -1, -1):
        if (int(num) & 2**(i)) == (2**i):
            r.append('T')
        else:
            r.append('F')
    return r

def hash_tobitb(num):
    h = hash_tobitl(num)
    r = []
    for i in range(0, len(h)//8):
        for j in range(((i+1)*8) - 1, (i*8) - 1, -1):
            r.append(h[j])
    return list(reversed(r))

def hash_tonum(bit):
    num = 0
    pos = 0
    for i in range(len(bit) - 1, -1, -1):
        if bit[i] == 'T':
            num += (1 << (31 - i))
    return num

def hash_tonum_correct(bit):
    cb = []
    order = []

    assert(len(bit) % 8 == 0)
    for i in range((len(bit) // 8) - 1, -1, -1):
        for j in range(0, 8):
            order.append((8*i)+j)

    for i in order:
        cb.append(bit[i])
    return hash_tonum(cb)
