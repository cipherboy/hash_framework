from hash_framework import attacks
from hash_framework.models import models

def constraints(algo, cols):
    # Differential Path
    differential = ['and']
    for i in range(0, algo.rounds):
        s = set([cols[j]['ri' + str(i)] for j in range(0, len(cols))])
        dlist = []
        for e in s:
            dlist.append([e, 'h1i', i*algo.int_size, "h2i", i*algo.int_size])
        differential.append(models.vars.choice_differentials(dlist))

    models.vars.write_clause('cdifferentials', tuple(differential), "07-differential.txt")

def model(algo, model, cols, generate=False):
    models.vars.write_header()

    if type(cols) == dict:
        cols = [cols]
    assert(type(cols) == list and len(cols) > 0 and type(cols[0]) == dict)
    prefixes=['h1', 'h2']

    if generate:
        models.generate(algo, prefixes)

    for prefix in prefixes:
        s = attacks.collision.get_state(algo, cols[0], prefix)
        models.vars.write_values(s, prefix + 's', "01-" + prefix + "-state.txt")

    attacks.collision.loose.constraints(algo, cols)
    attacks.collision.write_constraints(algo)
    attacks.collision.write_optional_differential(algo)
    models.vars.write_assign(['ccollision', 'cblocks', 'cdifferentials'])
