from hash_framework.models import models


def write_constraints(algo, prefixes=['h1', 'h2'], name="98-collision.txt", out_name="ccollision"):
    assert(type(prefixes) == list and len(prefixes) == 2 and type(prefixes[0]) == str and type(prefixes[1]) == str)
    c = ['and']
    for var in algo.output_vars:
        c.append(('equal', prefixes[0] + var, prefixes[1] + var))
    models.vars.write_clause(out_name, tuple(c), name)

def write_optional_differential(algo, prefixes=['h1', 'h2'], name="06-blocks.txt", out_name="cblocks"):
    assert(type(prefixes) == list and len(prefixes) == 2 and type(prefixes[0]) == str and type(prefixes[1]) == str)
    c = ['and']
    for var in algo.block_vars:
        c.append(('equal', prefixes[0] + var, prefixes[1] + var))
    models.vars.write_clause(out_name, ('not', tuple(c)), name)

def write_same_state(algo, prefixes=['h1', 'h2'], name="01-state.txt", out_name="cstate"):
    assert(type(prefixes) == list and len(prefixes) == 2 and type(prefixes[0]) == str and type(prefixes[1]) == str)
    c = ['and']
    for var in algo.state_vars:
        c.append(('equal', prefixes[0] + var, prefixes[1] + var))
    models.vars.write_clause(out_name, tuple(c), name)

def write_same_blocks(algo, prefixes=['h1', 'h2'], name="08-blocks.txt", out_name="cblock"):
    assert(type(prefixes) == list and len(prefixes) == 2 and type(prefixes[0]) == str and type(prefixes[1]) == str)
    c = ['and']
    for var in algo.block_vars:
        c.append(('equal', prefixes[0] + var, prefixes[1] + var))
    models.vars.write_clause(out_name, tuple(c), name)


def write_ascii_constraints(prefixes=['h1b'], count=64, name="44-ascii.txt"):
    z = "cascii := AND(T==T,"
    for i in range(0, count):
        b = i*8
        for prefix in prefixes:
            z += "NOT(" + prefix + str(b) + "),"
            z += "OR(" + prefix + str(b+1) + ", " + prefix + str(b+2) + "),"

    z += "T==T);"

    f = open(name, 'w')
    f.write(z)
    f.write("\n\n")
    f.flush()
    f.close()
