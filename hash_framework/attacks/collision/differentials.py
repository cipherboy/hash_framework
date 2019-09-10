from hash_framework import attacks
from hash_framework.models import models


def analyze(algo, cols):
    count = algo.block_size // algo.int_size
    differentials = []
    for i in range(0, count):
        differentials.append(set())
    for i in range(0, count):
        k = "db" + str(i)
        for col in cols:
            differentials[i].add(col[k])
    return differentials


def negate(algo, cols, clause="cblocks", name="06-blocks.txt"):
    differentials = analyze(algo, cols)
    r = ["and"]
    for i in range(0, algo.block_size // algo.int_size):
        print(list(differentials[i]))
        dlist = []
        for e in differentials[i]:
            dlist.append([e, "h1b", i * algo.int_size, "h2b", i * algo.int_size])
        r.append(models.vars.choice_differentials(dlist))
    models.vars.write_clause(clause, ("not", tuple(r)), name)


def write(algo, differential, clause="cblocks", name="06-blocks.txt"):
    delta = "".join(differential)
    r = models.vars.differential(delta, "h1b", 0, "h2b", 0)
    models.vars.write_clause(clause, r, name)


def write_path(algo, differential, clause="cdifferentials", name="09-differential.txt"):
    delta = "".join(differential)
    r = models.vars.differential(delta, "h1i", 0, "h2i", 0)
    models.vars.write_clause(clause, r, name)


def write_choice(algo, differentials, clause="cblocks", name="06-blocks.txt"):
    r = ["or"]
    for differential in differentials:
        delta = "".join(differential)
        r.append(models.vars.differential(delta, "h1b", 0, "h2b", 0))
    models.vars.write_clause(clause, tuple(r), name)


def expand(algo, db, cols, tag="md4-wangs-differentials"):
    i = 0
    dbcols = attacks.collision.load_db_tag(algo, db, tag)
    while True:
        m = models()
        m.start(tag + "-expand-r1", False)
        models.vars.write_header()
        if i == 0:
            models.generate(algo, ["h1", "h2"])
        i += 1

        attacks.collision.tight.constraints(algo, cols)
        attacks.collision.write_constraints(algo)
        attacks.collision.differentials.negate(algo, cols + dbcols)
        models.vars.write_assign(["ccollision", "cblocks", "cdifferentials"])
        m.collapse()
        m.build()
        sat = m.run(count=1)
        if not sat:
            break
        rs = m.results(algo)
        attacks.collision.insert_db_multiple(algo, db, rs, tag)
        dbcols = attacks.collision.load_db_tag(algo, db, tag)
    db.commit()
    return dbcols


def expand_loose(algo, db, cols, tag="md4-wangs-differentials"):
    i = 0
    dbcols = attacks.collision.load_db_tag(algo, db, tag)
    while True:
        m = models()
        m.start(tag + "-expand-r2", False)
        models.vars.write_header()
        if i == 0:
            models.generate(algo, ["h1", "h2"])
        i += 1

        attacks.collision.loose.constraints(algo, cols)
        attacks.collision.write_constraints(algo)
        attacks.collision.differentials.negate(algo, cols + dbcols)
        models.vars.write_assign(["ccollision", "cblocks", "cdifferentials"])
        m.collapse()
        m.build()
        sat = m.run(count=1)
        if not sat:
            break
        rs = m.results(algo)
        attacks.collision.insert_db_multiple(algo, db, rs, tag)
        dbcols = attacks.collision.load_db_tag(algo, db, tag)
    db.commit()
    return dbcols


def complete(algo, db, cols, tag):
    differentials = attacks.collision.differentials.analyze(algo, cols)
    i = 0
    for differential in itertools.product(*differentials):
        m = models()
        m.start(tag, False)
        models.vars.write_header()
        models.generate(algo, ["h1", "h2"])
        attacks.collision.tight.constraints(algo, cols)
        attacks.collision.write_constraints(algo)
        attacks.collision.differentials.write(algo, differential)
        models.vars.write_assign(["ccollision", "cblocks", "cdifferentials"])
        m.collapse()
        m.build()
        m.run(count=1)
        rs = m.results(algo)
        attacks.collision.insert_db_multiple(algo, db, rs, tag)
        i += 1
