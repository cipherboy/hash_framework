from hash_framework.boolean.simplify import *
from hash_framework.boolean.translate import *
from hash_framework.boolean.core import *

def b_dedupe_list(prefix, l):
    # We assume l is iterable; if x is a string, x[i] is a string
    # so it won't be deduped. Only nested tuple/list is deduped.
    o = []
    for i in range(0, len(l)):
        if type(l[i]) != str:
            o.append(clause_dedupe(l[i], prefix))
        else:
            o.append(l[i])

    return o

# Full adder carry bit
def b_fac(x, y, c):
    return simplify(b_or(b_and(x, y), b_and(c, b_or(x, y))))

# Full adder output bit
def b_fav(x, y, c):
    return simplify(b_xor(b_xor(x, y), c))

# Ripple carry adder, n bits
def b_rca(prefix, x, y, c="F"):
    assert(len(x) == len(y))

    # Dedupe x, y
    x = b_dedupe_list(prefix, x)
    y = b_dedupe_list(prefix, y)

    r = []
    for i in range(len(x) - 1, -1, -1):
        r = [clause_dedupe(b_fav(x[i], y[i], c), prefix)] + r
        c = clause_dedupe(b_fac(x[i], y[i], c), prefix)

    return r, c

def b_cla_carry(p, g, i):
    o = ['or', 'F']
    for j in range(0, i+1):
        b = ['and', 'T', g[j]]
        for k in range(j, i):
            b.append(p[k])
        o.append(simplify(tuple(b)))

    return simplify(tuple(o))

# Carry Lookahead Adder
def b_cla(prefix, x, y, c="F"):
    assert(len(x) == len(y))

    # Dedupe x, y
    x = b_dedupe_list(prefix, x)
    y = b_dedupe_list(prefix, y)

    p = []
    g = []
    for i in range(0, len(x)):
        p.append(clause_dedupe(b_xor(x[i], y[i]), prefix))
        g.append(clause_dedupe(b_and(x[i], y[i]), prefix))

    g.reverse()
    g = [c] + g
    p.reverse()

    cs = []
    for i in range(0, len(x)+1):
        cs.append(clause_dedupe(b_cla_carry(p, g, i), prefix))

    r = []
    for i in range(0, len(x)):
        r = [clause_dedupe(b_xor(p[i], cs[i]), prefix)] + r

    return r, cs[len(x)]

# Carry Select Adder
def b_csa(prefix, x, y, c="F", adder_func=b_rca):
    assert(len(x) == len(y))

    # Dedupe x, y
    x = b_dedupe_list(prefix, x)
    y = b_dedupe_list(prefix, y)

    layer_one, carry_one = adder_func(prefix, x, y, "F")
    layer_two, carry_two = adder_func(prefix, x, y, "T")

    r = []
    for i in range(0, len(layer_one)):
        r.append(clause_dedupe(b_mux(layer_one[i], layer_two[i], c), prefix))

    carry_out = clause_dedupe(b_mux(carry_one, carry_two, c), prefix)
    return r, carry_out
