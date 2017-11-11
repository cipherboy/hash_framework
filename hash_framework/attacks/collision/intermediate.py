from hash_framework import attacks
from hash_framework.models import models

def analyze(algo, cols):
    intermediate = []
    for i in range(0, algo.rounds):
        intermediate.append(set())

    for i in range(0, algo.rounds):
        k = 'ri' + str(i)
        for col in cols:
            intermediate[i].add(col[k])
    return intermediate

def write(algo, intermediates):
    # Differential Path
    differential = ['and']
    for j in range(0, algo.rounds):
        dlist = []
        for e in intermediates[j]:
            dlist.append([e, 'h1i', j*algo.int_size, "h2i", j*algo.int_size])
        differential.append(models.vars.choice_differentials(dlist))

    models.vars.write_clause('cdifferentials', tuple(differential), "07-differential.txt")

def write_negated(algo, intermediates):
    if len(intermediates) == 0:
        return
    # Differential Path
    differential = ['and']
    for j in range(0, algo.rounds):
        dlist = []
        for e in intermediates[j]:
            dlist.append([e, 'h1i', j*algo.int_size, "h2i", j*algo.int_size])
        differential.append(models.vars.choice_differentials(dlist))

    models.vars.write_clause('cnegated', ('not', tuple(differential)), "93-negated.txt")

def expand(algo, db, stuck, intermediate):
    m = models()
    for i in range(0, algo.rounds):
        # Don't write constraints for the four previous rounds
        # and four following rounds

        cols = attacks.collision.load_db_tag(algo, db, "md4-wangs-original")
        tag = "md4-wangs-intermediate-r1-" + str(i) + "-" + str(len(intermediate[i]))
        m.start(tag, False)
        models.vars.write_header()
        models.generate(algo, ['h1', 'h2'])
        # Differential Path
        differential = ['and']
        for j in range(0, algo.rounds):
            dlist = []
            if i == j:
                for e in intermediate[j]:
                    dlist.append([e, 'h1i', j*algo.int_size, "h2i", j*algo.int_size])
                differential.append(('not', models.vars.choice_differentials(dlist)))
                continue
            elif i-4 <= j <= i+4:
                continue
            for e in intermediate[j]:
                dlist.append([e, 'h1i', j*algo.int_size, "h2i", j*algo.int_size])
            differential.append(models.vars.choice_differentials(dlist))

        models.vars.write_clause('cdifferentials', tuple(differential), "07-differential.txt")
        attacks.collision.write_constraints(algo)
        attacks.collision.write_optional_differential(algo)
        attacks.collision.stuck.write(algo, stuck)
        models.vars.write_assign(['ccollision', 'cblocks', 'cdifferentials', 'cstuck'])
        m.collapse()
        m.build()
        m.run(count=10)
        rs = m.results(algo)
        attacks.collision.insert_db_multiple(algo, db, rs, tag)
