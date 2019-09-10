def find_neighbors(algo, db, start, rounds, tag):
    r = rounds
    algo.rounds = rounds
    cols = [start.copy()]
    attacks.collision.insert_db_multiple(algo, db, cols, tag + "-original")
    wq = []
    for i in range(0, rounds):
        wq.append((i))

    jq = []

    while len(wq) > 0:
        print(wq)
        i = wq.pop(0)

        m = models()
        m.start(tag + "-r" + str(i), False)
        models.vars.write_header()
        models.generate(algo, ["h1", "h2"], rounds=r, bypass=True)
        attacks.collision.connected.loose.constraints_new_neighbor(algo, cols, i)
        attacks.collision.write_same_state(algo)
        attacks.collision.write_constraints(algo)
        attacks.collision.write_optional_differential(algo)
        models.vars.write_assign(["cstate", "ccollision", "cblocks", "cdifferentials"])
        m.collapse()
        m.build()
        jqj = compute.perform_sat("problem.cnf", "problem.out", count=1, no_wait=True)
        jq.append((i, jqj))

        while compute.assign_work() is None or (len(wq) == 0 and len(jq) > 0):
            print("Waiting for work...")
            fj = compute.wait_job_hosts(loop_until_found=True)
            fj_status = fj[0]
            fj_job = fj[1]
            for j in range(0, len(jq)):
                jqe = jq[j]
                jqr = jqe[0]
                jqj = jqe[1]
                if jqj[0] == fj_job[0]:
                    print("Found finished job:")
                    print((fj, jqe))
                    if fj_status:
                        m = models()
                        m.start(tag + "-r" + str(jqr), False)
                        rs = m.results(algo)
                        ncols = attacks.collision.build_col_rows(algo, db, rs, tag)
                        cols.extend(ncols)
                        wq.append(jqr)
                    jq.remove(jq[j])
                    break

    attacks.collision.insert_db_multiple(algo, db, cols[1:], tag)
    return cols
