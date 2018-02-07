#!/usr/bin/env python3
from hash_framework.boolean import *

def __main__(a=[], b=[], prefix='cla', fname='03-cla-2x-4bits.txt'):
    assert(len(a) == len(b) and (len(a) % 4) == 0)
    f = open(fname, 'w')
    c = 'F'
    s = []

    for i in range(len(a)//4 - 1, -1, -1):
        in_a = a[i*4:(i+1)*4]
        in_b = b[i*4:(i+1)*4]
        ns, nc = cla_add_4bits(in_a, in_b, prefix, c)
        s = ns + s
        c = nc

    global clause_dedupe_s

    for k in clause_dedupe_s:
        if k[0:len(prefix)] == prefix:
            f.write(k + " := " + translate(clause_dedupe_s[k]) + ";\n")

    for i in range(0, len(s)):
        f.write(prefix + "s" + str(i) + " := " + translate(s[i]) + ";\n")


    f.close()


def cla_add_4bits(a, b, prefix, c):
    s = []

    nc = ('not', c)
    to1 = ('not', ('or', a[3], b[3]))
    ta1 = ('not', ('and', a[3], b[3]))
    to2 = ('not', ('or', a[2], b[2]))
    ta2 = ('not', ('and', a[2], b[2]))
    to3 = ('not', ('or', a[1], b[1]))
    ta3 = ('not', ('and', a[1], b[1]))
    to4 = ('not', ('or', a[0], b[0]))
    ta4 = ('not', ('and', a[0], b[0]))
    m0 = ('not', nc)
    m1 = ('and', ('not', to1), ta1)
    m2 = ('and', nc, ta1)
    m3 = to1
    m4 = ('and', ('not', to2), ta2)
    m5 = ('and', nc, ta1, ta2)
    m6 = ('and', ta2, to1)
    m7 = to2
    m8 = ('and', ('not', to3), ta3)
    m9 = ('and', nc, ta1, ta2, ta3)
    m10 = ('and', ta2, ta3, to1)
    m11 = ('and', ta3, to2)
    m12 = to3
    m13 = ('and', ('not', to4), ta4)
    m14 = ('and', nc, ta1, ta2, ta3, ta4)
    m15 = ('and', ta2, ta3, ta4, to1)
    m16 = ('and', ta3, ta4, to2)
    m17 = ('and', ta4, to3)
    m18 = to4

    s1 = ('xor', m0, m1)
    s2 = ('xor', ('not', ('or', m2, m3)), m4)
    s3 = ('xor', ('not', ('or', m5, m6, m7)), m8)
    s4 = ('xor', ('not', ('or', m9, m10, m11, m12)), m13)
    co = ('not', ('or', m14, m15, m16, m17, m18))

    s = [clause_dedupe(simplify(s1), prefix)] + s
    s = [clause_dedupe(simplify(s2), prefix)] + s
    s = [clause_dedupe(simplify(s3), prefix)] + s
    s = [clause_dedupe(simplify(s4), prefix)] + s
    co = clause_dedupe(simplify(co), prefix)

    return (s, co)

