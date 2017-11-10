def find_arbitrary_differential(algo, db, rounds, tag):
    algo.rounds = rounds
    m = models()
    m.start(tag, False)
    models.vars.write_header()
    models.generate(algo, ['h1', 'h2'], rounds=rounds, bypass=True)
    attacks.collision.write_same_state(algo)
    attacks.collision.write_constraints(algo)
    attacks.collision.write_optional_differential(algo)
    models.vars.write_assign(['ccollision', 'cblocks', 'cstate'])
    m.collapse()
    m.build()
    m.remote = False
    m.run(count=1)
    rs = m.results(algo)
    ncols = attacks.collision.build_col_rows(algo, db, rs, tag)
    print(ncols)

def only_one_differences(algo):
    differential = ['or']
    for i in range(0, algo.rounds):
        dlist = []
        for j in range(0, algo.rounds):
            if i == j:
                dlist.append(['i'*32, 'h1i', j*algo.int_size, "h2i", j*algo.int_size])
            else:
                dlist.append(['.'*32, 'h1i', j*algo.int_size, "h2i", j*algo.int_size])
        differential.append(models.vars.differentials(dlist))
    models.vars.write_clause('cdifferentials', tuple(differential), "07-differential.txt")

def only_two_differences(algo):
    differential = ['or']
    for i in range(0, algo.rounds):
        for k in range(i+1, algo.rounds):
            dlist = []
            for j in range(0, algo.rounds):
                if i == j:
                    dlist.append(['i'*32, 'h1i', j*algo.int_size, "h2i", j*algo.int_size])
                elif k == j:
                    dlist.append(['i'*32, 'h1i', j*algo.int_size, "h2i", j*algo.int_size])
                else:
                    dlist.append(['.'*32, 'h1i', j*algo.int_size, "h2i", j*algo.int_size])
            differential.append(models.vars.differentials(dlist))
    models.vars.write_clause('cdifferentials', tuple(differential), "07-differential.txt")

def specified_difference(algo, places):
    differential = ['and']
    for i in range(0, algo.rounds):
        if i not in places:
            differential.append(models.vars.differential('.'*32, 'h1i', i*algo.int_size, "h2i", i*algo.int_size))
        else:
            differential.append(models.vars.any_difference(32, 'h1i', i*algo.int_size, "h2i", i*algo.int_size))

    models.vars.write_clause('cdifferentials', tuple(differential), "07-differential.txt")

def find_simplest_differential(algo, db, rounds, tag):
    algo.rounds = rounds
    m = models()
    m.remote = False

    m.start(tag, False)
    models.vars.write_header()
    models.generate(algo, ['h1', 'h2'], rounds=rounds, bypass=True)
    attacks.collision.write_same_state(algo)
    attacks.collision.write_constraints(algo)
    attacks.collision.write_optional_differential(algo)
    attacks.collision.reduced.only_one_difference(algo)
    found_collisions = []
    found_differences = []

    while True:
        print(len(found_collisions))
        if len(found_collisions) > 0:
            found_differences = attacks.collision.intermediate.analyze(algo, found_collisions)
            print(found_differences)
            attacks.collision.intermediate.write_negated(algo, found_differences)
        models.vars.write_assign(['ccollision', 'cblocks', 'cstate', 'cdifferentials', 'cnegated'])
        m.collapse()
        m.build()
        sat = m.run(count=1)
        if not sat:
            break
        rs = m.results(algo)
        ncols = attacks.collision.build_col_rows(algo, db, rs, tag)
        found_collisions.append(ncols[0])
    print(found_differences)
    return found_differences

def parallel_simple_differentials(algo, db, rounds, sizes, tag_base):
    wq = []
    jq = []
    found_collisions = {}
    found_differences = {}
    print("Starting to generate work queue")
    for r in rounds:
        m = models()
        tag = tag_base + "-r" + str(r)
        m.start(tag, False)
        models.vars.write_header()
        models.generate(algo, ['h1', 'h2'], rounds=r, bypass=True)
        attacks.collision.write_same_state(algo)
        attacks.collision.write_constraints(algo)
        attacks.collision.write_optional_differential(algo)
        models.vars.write_assign(['ccollision', 'cblocks', 'cstate', 'cdifferentials', 'cnegated'])
        for s in sizes:
            for e in itertools.combinations(list(range(0, r)), s):
                algo.rounds = r
                m = models()
                tag = tag_base + "-r" + str(r) + "-s" + str(s) + "-e" + '-'.join(list(map(str, e)))
                m.start(tag, False)
                os.system("cp -r " + m.model_dir + "/" + tag_base + "-r" + str(r) + "/* " + m.model_dir + "/" + tag + "/")
                attacks.collision.reduced.specified_difference(algo, e)
                wq.append((r, s, e))
                found_differences[(r, s, e)] = []
    print("Done generating work...")
    print("Running work...")
    random.shuffle(wq)
    while len(wq) > 0:
        w = wq.pop(0)
        print("wq: " + str(len(wq)))
        print("jq: " + str(len(jq)))
        print("Handling job: " + str(w))
        r = w[0]
        s = w[1]
        e = w[2]
        algo.rounds = r
        m = models()
        tag = tag_base + "-r" + str(r) + "-s" + str(s) + "-e" + '-'.join(list(map(str, e)))
        m.start(tag, False)
        if len(found_differences[w]) > 0:
            print(found_differences[w])
            attacks.collision.intermediate.write_negated(algo, found_differences[w])
        m.collapse()
        m.build()
        j = compute.perform_sat("problem.cnf", "problem.out", count=1, no_wait=True, ident=(w))
        jq.append((w, j))
        print("Done handling job.")

        while compute.assign_work() is None or (len(wq) == 0 and len(jq) > 0):
            print("Waiting for work...")
            fj = compute.wait_job_hosts(loop_until_found=True)
            fj_status = fj[0]
            fj_job = fj[1]
            fj_w = fj_job[6]
            found = False
            for j in range(0, len(jq)):
                jqe = jq[j]
                jqw = jqe[0]
                jqj = jqe[1]
                if fj_w == jqw:
                    print("Found finished job:")
                    found = True
                    if fj_status:
                        w = fj_w
                        print(w)
                        #wq.append(w)
                        r = fj_w[0]
                        s = fj_w[1]
                        e = fj_w[2]
                        algo.rounds = r
                        m = models()
                        tag = tag_base + "-r" + str(r) + "-s" + str(s) + "-e" + '-'.join(list(map(str, e)))
                        m.start(tag, False)
                        rs = m.results(algo)
                        ncols = attacks.collision.build_col_rows(algo, db, rs, tag)
                        if len(ncols) < 1:
                            continue
                        attacks.collision.insert_db_multiple(algo, db, ncols, tag)
                        db.commit()
                        nfd = attacks.collision.intermediate.analyze(algo, ncols)
                        if len(found_differences[w]) == 0:
                            found_differences[w] = nfd
                        else:
                            for i in range(0, len(nfd)):
                                for ele in nfd[i]:
                                    found_differences[w][i].add(ele)

                    jq.remove(jq[j])
                    break


            if not found:
                print("Did not find job..." + str(jq) + " || " + str(fj))
            print("Done waiting for work.")

    print(found_differences)

def generate_test_delta(d, n, r):
    if n <= 0:
        return [tuple(d)]
    res = []
    ds = set(d)
    for e in itertools.combinations(list(range(0, r)), n):
        es = set(e)
        if len(es.intersection(ds)) == 0:
            n = list(ds.union(es))
            n.sort()
            res.append(tuple(n))
    return res

def find_extended(algo, db, delta_set, rounds, tag_base):
    nd = []
    wq = []
    jq = []
    found_differences = {}

    r = rounds
    algo.rounds = r

    m = models()
    tag = tag_base + "-r" + str(r)
    m.start(tag, False)
    models.vars.write_header()
    models.generate(algo, ['h1', 'h2'], rounds=r, bypass=True)
    attacks.collision.write_same_state(algo)
    attacks.collision.write_constraints(algo)
    attacks.collision.write_optional_differential(algo)
    models.vars.write_assign(['ccollision', 'cblocks', 'cstate', 'cdifferentials', 'cnegated'])

    print("Generating work queue...")
    for deltas in delta_set:
        for n in range(0, 1):
            wd = attacks.collision.reduced.generate_test_delta(deltas, n, rounds)
            print(wd)
            print(type(wd[0]))
            for e in wd:
                m = models()
                s = len(e)
                tag = tag_base + "-r" + str(r) + "-s" + str(s) + "-e" + '-'.join(list(map(str, e)))
                m.start(tag, False)
                os.system("cp -r " + m.model_dir + "/" + tag_base + "-r" + str(r) + "/* " + m.model_dir + "/" + tag + "/")
                attacks.collision.reduced.specified_difference(algo, e)
                wq.append((r, s, e))
                found_differences[(r, s, e)] = []
                m.collapse()
                m.build()

    print("Finished generating work queue...")
    random.shuffle(wq)
    print("Running work...")
    while len(wq) > 0:
        w = wq.pop(0)
        print("wq: " + str(len(wq)))
        print("jq: " + str(len(jq)))
        print("Handling job: " + str(w))
        r = w[0]
        s = w[1]
        e = w[2]
        algo.rounds = r
        m = models()
        tag = tag_base + "-r" + str(r) + "-s" + str(s) + "-e" + '-'.join(list(map(str, e)))
        m.start(tag, False)
        j = compute.perform_sat("problem.cnf", "problem.out", count=1, no_wait=True, ident=(w))
        jq.append((w, j))
        print("Done handling job.")

        while compute.assign_work() is None or (len(wq) == 0 and len(jq) > 0):
            print("Waiting for work...")
            print(len(jq))
            fj = compute.wait_job_hosts(loop_until_found=True)
            fj_status = fj[0]
            fj_job = fj[1]
            fj_w = fj_job[6]
            found = False
            for j in range(0, len(jq)):
                jqe = jq[j]
                jqw = jqe[0]
                jqj = jqe[1]
                if fj_w == jqw:
                    print("Found finished job:")
                    print(fj_w)
                    print(fj_status)
                    found = True
                    if fj_status:
                        w = fj_w
                        #wq.append(w)
                        r = fj_w[0]
                        s = fj_w[1]
                        e = fj_w[2]
                        algo.rounds = r
                        m = models()
                        tag = tag_base + "-r" + str(r) + "-s" + str(s) + "-e" + '-'.join(list(map(str, e)))
                        m.start(tag, False)
                        rs = m.results(algo)
                        ncols = attacks.collision.build_col_rows(algo, db, rs, tag)
                        if len(ncols) < 1:
                            continue
                        attacks.collision.insert_db_multiple(algo, db, ncols, tag)
                        db.commit()
                        nfd = attacks.collision.intermediate.analyze(algo, ncols)
                        if len(found_differences[w]) == 0:
                            found_differences[w] = nfd
                        else:
                            for i in range(0, len(nfd)):
                                for ele in nfd[i]:
                                    found_differences[w][i].add(ele)

                    jq.remove(jq[j])
                    break


            if not found:
                print("Did not find job..." + str(jq) + " || " + str(fj))
            print("Done waiting for work.")

    print(found_differences)

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
        m.start(tag+"-r" + str(i), False)
        models.vars.write_header()
        models.generate(algo, ['h1', 'h2'], rounds=r, bypass=True)
        attacks.collision.connected.loose.constraints_new_neighbor(algo, cols, i)
        attacks.collision.write_same_state(algo)
        attacks.collision.write_constraints(algo)
        attacks.collision.write_optional_differential(algo)
        models.vars.write_assign(['cstate', 'ccollision', 'cblocks', 'cdifferentials'])
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
