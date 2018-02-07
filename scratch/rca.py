#!/usr/bin/env python3

from hash_framework.boolean import *

def __main__(a=[], b=[], prefix="rca", fname='02-rca-2x-4bits.txt'):
    f = open(fname, 'w')

    c = 'F'
    s = []

    for i in range(len(a) - 1, -1, -1):
        s = [clause_dedupe(simplify(('xor', a[i], b[i], c)), prefix)] + s
        c = clause_dedupe(simplify(('xor', ('and', a[i], b[i]), ('and', a[i], c), ('and', b[i], c))), prefix)

    global clause_dedupe_s

    for k in clause_dedupe_s:
        if k[0:len(prefix)] == prefix:
            f.write(k + " := " + translate(clause_dedupe_s[k]) + ";\n")

    for i in range(0, len(s)):
        f.write(prefix + "s" + str(i) + " := " + translate(s[i]) + ";\n")


    f.close()
