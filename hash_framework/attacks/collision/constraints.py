from hash_framework import models

def write_constraints(algo, prefixes=['h1', 'h2'], name="98-collision.txt"):
    assert(type(prefixes) == list and len(prefixes) == 2 and type(prefixes[0]) == str and type(prefixes[1]) == str)
    c = ['and']
    for var in algo.output_vars:
        c.append(('equal', prefixes[0] + var, prefixes[1] + var))
    models.vars.write_clause("ccollision", tuple(c), name)

def write_optional_differential(algo, prefixes=['h1', 'h2'], name="06-blocks.txt"):
    assert(type(prefixes) == list and len(prefixes) == 2 and type(prefixes[0]) == str and type(prefixes[1]) == str)
    c = ['and']
    for var in algo.block_vars:
        c.append(('equal', prefixes[0] + var, prefixes[1] + var))
    models.vars.write_clause("cblocks", ('not', tuple(c)), name)

def write_same_state(algo, prefixes=['h1', 'h2'], name="01-state.txt"):
    assert(type(prefixes) == list and len(prefixes) == 2 and type(prefixes[0]) == str and type(prefixes[1]) == str)
    c = ['and']
    for var in algo.state_vars:
        c.append(('equal', prefixes[0] + var, prefixes[1] + var))
    models.vars.write_clause("cstate", tuple(c), name)
