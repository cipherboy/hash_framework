#!/usr/bin/python

from hash_framework.boolean.simplify import *
from hash_framework.boolean.translate import *

def b_and(x, y):
    return simplify(('and', x, y))

def b_or(x, y):
    return simplify(('or', x, y))

def b_not(x):
    return simplify(('not', x))

def b_xor(x, y):
    #return simplify(b_or(b_and(x, b_not(y)), b_and(b_not(x), y)))
    return simplify(('xor', x, y))

def b_xorw(x, y):
    r = []
    assert(len(x) == len(y))
    for i in range(0, len(x)):
        r.append(b_xor(x[i], y[i]))

    return r

def b_andbit(b, x):
    r = []
    for i in range(0, len(x)):
        r.append(b_and(b, x[i]))
    return r

def b_fac(x, y, c):
    return simplify(b_or(b_and(x, y), b_and(c, b_or(x, y))))

def b_fav(x, y, c):
    return simplify(b_xor(b_xor(x, y), c))

def b_addl(x, y):
    c = "F"
    r = []
    assert(len(x) == len(y)) # Assert fixed-sized numbers
    for i in range(len(x) - 1, -1, -1):
        r.append(simplify(b_fav(x[i], y[i], c)))
        c = simplify(b_fac(x[i], y[i], c))
    r.reverse()
    return r

def b_fav4(c0, c1, x1, x2, x3, x4):
    return simplify(('xor', c0, c1, x1, x2, x3, x4))

def b_fac4(c0, c1, x1, x2, x3, x4):
    return simplify(('or', ('and', ('not', x1), ('not', x2), ('not', x3), ('not', x4), c0, c1), ('and', ('not', x1), ('not', x2), ('not', x3), x4, ('not', c0), c1), ('and', ('not', x1), ('not', x2), ('not', x3), x4, c0, ('not', c1)), ('and', ('not', x1), ('not', x2), ('not', x3), x4, c0, c1), ('and', ('not', x1), ('not', x2), x3, ('not', x4), ('not', c0), c1), ('and', ('not', x1), ('not', x2), x3, ('not', x4), c0, ('not', c1)), ('and', ('not', x1), ('not', x2), x3, ('not', x4), c0, c1), ('and', ('not', x1), ('not', x2), x3, x4, ('not', c0), ('not', c1)), ('and', ('not', x1), ('not', x2), x3, x4, ('not', c0), c1), ('and', ('not', x1), ('not', x2), x3, x4, c0, ('not', c1)), ('and', ('not', x1), x2, ('not', x3), ('not', x4), ('not', c0), c1), ('and', ('not', x1), x2, ('not', x3), ('not', x4), c0, ('not', c1)), ('and', ('not', x1), x2, ('not', x3), ('not', x4), c0, c1), ('and', ('not', x1), x2, ('not', x3), x4, ('not', c0), ('not', c1)), ('and', ('not', x1), x2, ('not', x3), x4, ('not', c0), c1), ('and', ('not', x1), x2, ('not', x3), x4, c0, ('not', c1)), ('and', ('not', x1), x2, x3, ('not', x4), ('not', c0), ('not', c1)), ('and', ('not', x1), x2, x3, ('not', x4), ('not', c0), c1), ('and', ('not', x1), x2, x3, ('not', x4), c0, ('not', c1)), ('and', ('not', x1), x2, x3, x4, ('not', c0), ('not', c1)), ('and', x1, ('not', x2), ('not', x3), ('not', x4), ('not', c0), c1), ('and', x1, ('not', x2), ('not', x3), ('not', x4), c0, ('not', c1)), ('and', x1, ('not', x2), ('not', x3), ('not', x4), c0, c1), ('and', x1, ('not', x2), ('not', x3), x4, ('not', c0), ('not', c1)), ('and', x1, ('not', x2), ('not', x3), x4, ('not', c0), c1), ('and', x1, ('not', x2), ('not', x3), x4, c0, ('not', c1)), ('and', x1, ('not', x2), x3, ('not', x4), ('not', c0), ('not', c1)), ('and', x1, ('not', x2), x3, ('not', x4), ('not', c0), c1), ('and', x1, ('not', x2), x3, ('not', x4), c0, ('not', c1)), ('and', x1, ('not', x2), x3, x4, ('not', c0), ('not', c1)), ('and', x1, x2, ('not', x3), ('not', x4), ('not', c0), ('not', c1)), ('and', x1, x2, ('not', x3), ('not', x4), ('not', c0), c1), ('and', x1, x2, ('not', x3), ('not', x4), c0, ('not', c1)), ('and', x1, x2, ('not', x3), x4, ('not', c0), ('not', c1)), ('and', x1, x2, x3, ('not', x4), ('not', c0), ('not', c1)), ('and', x1, x2, x3, x4, c0, c1)))

def b_facc4(c0, c1, x1, x2, x3, x4):
    return simplify(('or', ('and', ('not', x1), ('not', x2), x3, x4, c0, c1), ('and', ('not', x1), x2, ('not', x3), x4, c0, c1), ('and', ('not', x1), x2, x3, ('not', x4), c0, c1), ('and', ('not', x1), x2, x3, x4, ('not', c0), c1), ('and', ('not', x1), x2, x3, x4, c0, ('not', c1)), ('and', ('not', x1), x2, x3, x4, c0, c1), ('and', x1, ('not', x2), ('not', x3), x4, c0, c1), ('and', x1, ('not', x2), x3, ('not', x4), c0, c1), ('and', x1, ('not', x2), x3, x4, ('not', c0), c1), ('and', x1, ('not', x2), x3, x4, c0, ('not', c1)), ('and', x1, ('not', x2), x3, x4, c0, c1), ('and', x1, x2, ('not', x3), ('not', x4), c0, c1), ('and', x1, x2, ('not', x3), x4, ('not', c0), c1), ('and', x1, x2, ('not', x3), x4, c0, ('not', c1)), ('and', x1, x2, ('not', x3), x4, c0, c1), ('and', x1, x2, x3, ('not', x4), ('not', c0), c1), ('and', x1, x2, x3, ('not', x4), c0, ('not', c1)), ('and', x1, x2, x3, ('not', x4), c0, c1), ('and', x1, x2, x3, x4, ('not', c0), ('not', c1)), ('and', x1, x2, x3, x4, ('not', c0), c1), ('and', x1, x2, x3, x4, c0, ('not', c1)), ('and', x1, x2, x3, x4, c0, c1)))

def b_add4l(eval_table, prefix, x1, x2, x3, x4):
    assert(len(x1) == len(x2))
    assert(len(x1) == len(x3))
    assert(len(x1) == len(x4))

    for i in range(0, len(x1)):
        if type(x1[i]) == tuple:
            var = clause_dedupe(simplify(x1[i]), prefix)
            x1[i] = var
        if type(x2[i]) == tuple:
            var = clause_dedupe(simplify(x2[i]), prefix)
            x2[i] = var
        if type(x3[i]) == tuple:
            var = clause_dedupe(simplify(x3[i]), prefix)
            x3[i] = var
        if type(x4[i]) == tuple:
            var = clause_dedupe(simplify(x4[i]), prefix)
            x4[i] = var

    r = []
    c0 = ["F"]*len(x1)
    c1 = ["F"]*len(x1)
    for i in range(len(x1) - 1, -1, -1):
        r.append(b_fav4(c0[i], c1[i], x1[i], x2[i], x3[i], x4[i]))
        nc0 = b_fac4(c0[i], c1[i], x1[i], x2[i], x3[i], x4[i])
        nc1 = b_facc4(c0[i], c1[i], x1[i], x2[i], x3[i], x4[i])
        if type(nc0) == tuple:
            var = clause_dedupe(simplify(nc0), prefix)
            nc0 = var
        if type(nc1) == tuple:
            var = clause_dedupe(simplify(nc1), prefix)
            nc1 = var
        c0[i-1] = nc0
        c1[i-2] = nc1
    r.reverse()
    return r, eval_table

def b_mul(a, b):
    assert(len(a) == len(b))
    adds = []
    for i in range(0, len(b)):
        pass

def b_rotl(x, l):
    return x[l:] + x[:l]

def b_rotr(x, l):
    x.reverse()
    x = b_rotl(x, l)
    x.reverse()
    return x

def b_tobitl(num):
    r = []
    for i in range(31, -1, -1):
        if (int(num) & 2**(i)) == (2**i):
            r.append('T')
        else:
            r.append('F')
    return r

def b_tobitb(num):
    h = b_tobitl(num)
    r = []
    for i in range(0, len(h)//8):
        for j in range(((i+1)*8) - 1, (i*8) - 1, -1):
            r.append(h[j])
    return list(reversed(r))

def b_tonum(bit):
    num = 0
    pos = 0
    for i in range(len(bit) - 1, -1, -1):
        if bit[i] == 'T':
            num += (1 << (31 - i))
    return num

def b_tonum_correct(bit):
    cb = []
    order = []

    assert(len(bit) % 8 == 0)
    for i in range((len(bit) // 8) - 1, -1, -1):
        for j in range(0, 8):
            order.append((8*i)+j)

    for i in order:
        cb.append(bit[i])
    return b_tonum(cb)
