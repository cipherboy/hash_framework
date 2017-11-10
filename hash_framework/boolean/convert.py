#!/usr/bin/env python

import sys
from hash_boolean import *

def circuit_vars(circuit):
    vars = []
    for l in circuit:
        if ":=" in l:
            vars.append(l.split(':=')[0].strip())
    return vars

def sat_vars(sat):
    vars = {}
    for l in sat:
        if len(l) > 0 and l[0] == 'c' and '<->' in l:
            vars[l[2:].split("<->")[0].strip()] = l[2:].split("<->")[1].strip()
    return vars

def main():
    circuit = open(sys.argv[1], 'r').read().split("\n")
    sat = open(sys.argv[2], 'r').read().split("\n")
    c_vars = circuit_vars(circuit)
    s_vars = sat_vars(sat)
    print(c_vars)
    print(s_vars)
    a = []
    b = []
    c = []
    d = []
    for i in range(0, 32):
        l = "oaa" + str(i)
        if l in s_vars:
            a.append(s_vars[l])
        else:
            a.append('T')
        l = "obb" + str(i)
        if l in s_vars:
            b.append(s_vars[l])
        else:
            b.append('T')
        l = "occ" + str(i)
        if l in s_vars:
            c.append(s_vars[l])
        else:
            c.append('T')
        l = "odd" + str(i)
        if l in s_vars:
            d.append(s_vars[l])
        else:
            d.append('T')
    print(hash_tonum(a))
    print(hash_tonum(b))
    print(hash_tonum(c))
    print(hash_tonum(d))


if __name__ == "__main__":
    main()
