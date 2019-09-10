from hash_framework import attacks
from hash_framework.models import models


def constraints(algo, cols):
    # Differential Path
    differential = ["and"]
    for i in range(0, algo.rounds):
        s = set([cols[j]["di" + str(i)] for j in range(0, len(cols))])
        dlist = []
        for e in s:
            dlist.append([e, "h1i", i * algo.int_size, "h2i", i * algo.int_size])
        differential.append(models.vars.choice_differentials(dlist))

    models.vars.write_clause(
        "cdifferentials", tuple(differential), "07-differential.txt"
    )


def model(algo, model, cols, generate=False):
    models.vars.write_header()

    if type(cols) == dict:
        cols = [cols]
    assert type(cols) == list and len(cols) > 0 and type(cols[0]) == dict
    prefixes = ["h1", "h2"]

    if generate:
        models.generate(algo, prefixes)

    for prefix in prefixes:
        s = attacks.collision.get_state(algo, cols[0], prefix)
        models.vars.write_values(s, prefix + "s", "01-" + prefix + "-state.txt")

    attacks.collision.tight.constraints(algo, cols)
    attacks.collision.write_constraints(algo)
    attacks.collision.write_optional_differential(algo)
    models.vars.write_assign(["ccollision", "cblocks", "cdifferentials"])


def parallel_extend(algo, db, cols, tag):
    m = models()
    m.start(tag, False)
    attacks.collision.tight.model(algo, m, cols, True)
    diffs = attacks.collision.differentials.analyze(algo, cols)
    attacks.collision.differentials.write_choice(algo, diffs)
    models.vars.write_values("".join(algo.default_state_bits), "h1s", "01-h1-state.txt")
    models.vars.write_values("".join(algo.default_state_bits), "h2s", "01-h2-state.txt")
    models.vars.write_assign(["ccollision", "cblocks", "cdifferentials"])
    m.collapse()
    m.build()
    jq = []
    fj = []
    i = 0
    job_max = 1000
    solutions_max = 100
    while i < job_max:
        while i < job_max and compute.assign_work() is not None:
            s = random.randint(0, 223212342)
            jq.append(
                compute.perform_sat(
                    "problem.cnf",
                    "problem-" + str(i) + ".out",
                    count=solutions_max,
                    seed=s,
                    no_wait=True,
                )
            )
            i += 1
        fj.append(compute.wait_job_hosts(loop_until_found=True))

    for j in jq:
        n_p = j[0]
        n_p.wait()

    print("DONE")
    # rs = m.results(algo)
    # attacks.collision.insert_db_multiple(algo, db, rs, tag)
