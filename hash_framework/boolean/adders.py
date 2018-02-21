from hash_framework.boolean.simplify import *
from hash_framework.boolean.translate import *
from hash_framework.boolean.core import *
from hash_framework.config import config

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

    assert(len(x) == len(layer_one))
    assert(len(x) == len(layer_two))

    r = []
    for i in range(0, len(layer_one)):
        r.append(clause_dedupe(b_mux(layer_one[i], layer_two[i], c), prefix))

    carry_out = clause_dedupe(b_mux(carry_one, carry_two, c), prefix)
    return r, carry_out

# Ripple Carry helper for b_addl
def b_addl_ripple_carry(prefix, x, y, c, e):
    if e["type"] == "rca":
        return b_rca(prefix, x, y, c=c)
    elif e["type"] == "cla":
        return b_cla(prefix, x, y, c=c)
    elif type(e["type"]) == "list":
        return b_addl(prefix, x, y, c=c, cfg=e["type"])
    else:
        assert(False)

# Carry Select helper for b_addl
def b_addl_carry_select(prefix, x, y, c, e):
    if e["type"] == "rca":
        return b_csa(prefix, x, y, c=c, adder_func=b_rca)
    elif e["type"] == "cla":
        return b_csa(prefix, x, y, c=c, adder_func=b_cla)
    elif type(e["type"]) == list:
        # Bind adder config to cfg in b_addl
        return b_csa(prefix, x, y, c=c, adder_func=b_addl)
    else:
        assert(False)

# Adder, with config
def b_addl(prefix, x, y, c="F", cfg=None):
    assert(len(x) == len(y))
    assert(type(cfg) == list or cfg == None)

    if cfg == None:
        cfg = config.default_adder

    # LSB = end - 1
    end = len(x)

    # Carry In: c

    r = []
    for e in cfg:
        start = 0
        if "width" in e:
            start = end - e["width"]
            if start < 0:
                start = 0

        i_x = x[start:end]
        i_y = y[start:end]
        n_r = []
        n_c = None

        if e["chaining"] == None or e["chaining"] == "ripple" or e["chaining"] == "rca":
            # Assume Ripple Carry
            n_r, n_c = b_addl_ripple_carry(prefix, i_x, i_y, c, e)
        elif e["chaining"] == "csa" or e["chaining"] == "select":
            n_r, n_c = b_addl_carry_select(prefix, i_x, i_y, c, e)

        if len(n_r) != len(i_x) or n_c == None or n_r == []:
            print("Bad adder")
            print((len(n_r), len(i_x), n_c, n_r))
            print(e)
            print(cfg)
            assert(False)

        r = n_r + r
        c = n_c

        end = start
        if end <= 0:
            break

    if len(r) != len(x):
        print("Bad config")
        assert(False)

    return r, c

def b_add4l(prefix, x1, x2, x3, x4, c="F", cfg=None):
    assert(type(cfg) == list or cfg == None)
    x1234v = []
    x1234c = None

    if cfg == None:
        cfg = config.default_adder

    if not 'shape' in cfg[0] or cfg[0]['shape'] == "tree":
        x12v, x12c = b_addl(prefix, x1, x2, c=c, cfg=default_adder)
        x34v, x34c = b_addl(prefix, x3, x4, c="F", cfg=default_adder)
        x1234v, x1234c = b_addl(prefix, x12, x34, c="F", cfg=default_adder)
    elif cfg[0]['shape'] == "incremental":
        x12v, x12c = b_addl(prefix, x1, x2, c=c, cfg=default_adder)
        x123v, x123c = b_addl(prefix, x12, x3, c="F", cfg=default_adder)
        x1234v, x1234c = b_addl(prefix, x123, x4, c="F", cfg=default_adder)
    else:
        assert(False)

    return x1234v, x1234c
