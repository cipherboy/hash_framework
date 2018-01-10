from hash_framework import *

def __main__():
    r = 36
    start_state = "FTTFFTTTFTFFFTFTFFTFFFTTFFFFFFFTTTTFTTTTTTFFTTFTTFTFTFTTTFFFTFFTTFFTTFFFTFTTTFTFTTFTTTFFTTTTTTTFFFFTFFFFFFTTFFTFFTFTFTFFFTTTFTTF"

    algo = algorithms.md4()
    algo.rounds = r

    db = hash_framework.database()

    m = models()
    m.remote = False

    m.start("md4-minimal-r" + str(r), False)
    models.vars.write_header()
    models.generate(algo, ['h1', 'h2'], rounds=r, bypass=True)

    attacks.collision.write_constraints(algo)
    attacks.collision.write_optional_differential(algo)
    attacks.collision.write_same_state(algo)

    if start_state != "":
        models.vars.write_values(start_state, 'h1s', "01-h1-state.txt")
        models.vars.write_values(start_state, 'h2s', "01-h2-state.txt")

    s = "cdifferentials := [2, 2]("
    for i in range(0, 32*r):
        s += "NOT(h1i" + str(i) + " == " + "h2i" + str(i) + "),"
    s = s[:-1] + ");\n\n"
    f = open("08-differential-path.txt", 'w')
    f.write(s)
    f.flush()
    f.close()

    models.vars.write_assign(['ccollision', 'cblocks', 'cstate', 'cdifferentials'])

    m.collapse(bc="problem.bc")
    m.build(bc="problem.bc", cnf="problem.cnf")

    r = m.run(count=1)
    if r:
        print("SAT")
        rs = m.results(algo)
        tag = "md4-minimal-r" + str(algo.rounds)
        attacks.collision.insert_db_multiple(algo, db, rs, tag)
        # print(rs)
    else:
        print("UNSAT")





__main__()
