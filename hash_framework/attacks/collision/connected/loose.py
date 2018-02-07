import hash_framework

class database:
    def setup(algo, db):
        # Create target queue
        q = hash_framework.attacks.collision.create_table_query(algo, "t_" + algo.name)
        db.execute(q)

        # Create neighborhood queue
        q = hash_framework.attacks.collision.create_table_query(algo, "wq_" + algo.name)
        db.execute(q)

        # Create results
        q = hash_framework.attacks.collision.create_table_query(algo, "r_" + algo.name)
        db.execute(q)

        # Current working set
        q = hash_framework.attacks.collision.create_table_query(algo, "ws_" + algo.name)
        db.execute(q)

        # Current edge list
        q = "CREATE TABLE g_" + algo.name + " (v1 INTEGER,  v2 INTEGER);"
        db.execute(q)

        db.commit()

    def populate(algo, db, start, target):
        hash_framework.attacks.collision.connected.loose.database.add(algo, db, start, "wq")
        hash_framework.attacks.collision.connected.loose.database.add(algo, db, start, "r")
        hash_framework.attacks.collision.connected.loose.database.add(algo, db, target, "t", True)
        hash_framework.attacks.collision.connected.loose.database.add(algo, db, target, "r", True)

    def pop(algo, db, prefix="wq"):
        name = prefix + "_" + algo.name

        cols = hash_framework.attacks.collision.table_cols(algo)
        cols.append('ROWID')

        r = db.query(name, cols, limit=1)
        if type(r) == dict:
            db.execute("DELETE FROM " + name + " WHERE ROWID=" + r['ROWID'] + ";")
            db.commit()
            return r

        return None

    def read(algo, db, prefix="wq"):
        name = prefix + "_" + algo.name

        cols = hash_framework.attacks.collision.table_cols(algo)
        cols.append('ROWID')

        r = db.query(name, cols, limit=1)
        if type(r) == dict:
            return r

        return None

    def add(algo, db, col, prefix="wq", commit=False):
        h1 = unprefix_keys(col, "h1")
        h1 = algo.to_hex(h1)
        #print_dict(h1, "h1")

        h2 = unprefix_keys(col, "h2")
        h2 = algo.to_hex(h2)
        #print_dict(h2, "h2")

        h1s = b_hex_to_block(h1['state'])
        h1b = b_hex_to_block(h1['block'])
        h2s = b_hex_to_block(h2['state'])
        h2b = b_hex_to_block(h2['block'])

        et = hash_framework.attacks.collision.build_col_row(algo, db, h1s, h1b, h2s, h2b, "")

        hash_framework.attacks.collision.__insert__(db, prefix + "_" + algo.name, et)

        if commit:
            db.commit()

    def count(algo, db, prefix="wq"):
        name = prefix + "_" + algo.name
        q = "SELECT COUNT(*) FROM " + name + ";"
        c = db.execute(q)
        r = c.fetchall()
        print(r)
        return r[0][0]

## end class -- database


def constraints(algo, start, step):
    # Differential Path
    differential = ['and']
    for i in range(0, algo.rounds):
        k = 'ri' + str(i)
        if i == step[0]:
            differential.append(models.vars.differential(step[2], 'h1i', i*algo.int_size, "h2i", i*algo.int_size))
        else:
            differential.append(models.vars.differential(start[k], 'h1i', i*algo.int_size, "h2i", i*algo.int_size))

    hash_framework.models.vars.write_clause('cdifferentials', tuple(differential), "07-differential.txt")

def any_unit_step(algo, start, target):
    pos = hash_framework.attacks.collision.metric.loose.delta(algo, start, target)
    all_differentials = ['or']
    for step in pos:
        differential = ['and']
        for i in range(0, algo.rounds):
            k = 'ri' + str(i)
            if i == step[0]:
                differential.append(models.vars.differential(step[2], 'h1i', i*algo.int_size, "h2i", i*algo.int_size))
            else:
                differential.append(models.vars.differential(start[k], 'h1i', i*algo.int_size, "h2i", i*algo.int_size))
        all_differentials.append(tuple(differential))
    hash_framework.models.vars.write_clause('cdifferentials', tuple(all_differentials), "07-differential.txt")

def new_unit_step(algo, start, cols, target):
    pos = hash_framework.attacks.collision.metric.loose.delta(algo, start, target)
    all_differentials = ['or']
    for step in pos:
        differential = ['and']
        for i in range(0, algo.rounds):
            k = 'ri' + str(i)
            if i == step[0]:
                differential.append(models.vars.differential(step[2], 'h1i', i*algo.int_size, "h2i", i*algo.int_size))
            else:
                differential.append(models.vars.differential(start[k], 'h1i', i*algo.int_size, "h2i", i*algo.int_size))
        all_differentials.append(tuple(differential))
    negated = ['and']
    for col in cols:
        differential = ['and']
        for i in range(0, algo.rounds):
            k = 'ri' + str(i)
            differential.append(models.vars.differential(col[k], 'h1i', i*algo.int_size, "h2i", i*algo.int_size))
        negated.append(tuple(differential))
    raw_target = ('and', tuple(all_differentials), ('not', tuple(negated)))
    hash_framework.models.vars.write_clause('cdifferentials', tuple(raw_target), "07-differential.txt")

def distributed_new_neighbor(algo, base, existing, poses, name="07-differential.txt", prefixes=["h1", 'h2'], out_name="cdifferentials"):
    assert(type(prefixes) == list or type(prefixes) == tuple)
    assert(len(prefixes) == 2)
    h1 = prefixes[0]
    h2 = prefixes[1]
    differential = ['and']
    for i in range(0, algo.rounds):
        k = "ri" + str(i)
        if i in poses:
            dlist = []
            for e in existing[i]:
                dlist.append([e, h1 + 'i', i*algo.int_size, h2 + 'i', i*algo.int_size])
            dlist.append([base[i], h1 + 'i', i*algo.int_size, h2 + 'i', i*algo.int_size])
            differential.append(('not', hash_framework.models.vars.choice_differentials(dlist)))
        else:
            differential.append(models.vars.differential(base[i], 'h1i', i*algo.int_size, 'h2i', i*algo.int_size))

    hash_framework.models.vars.write_clause(out_name, tuple(differential), name)

def constraints_new_neighbor(algo, cols, pos):
    # Differential Path
    differential = ['and']
    for i in range(0, algo.rounds):
        k = 'ri' + str(i)
        if i == pos:
            dlist = []
            dlist2 = set()
            for e in cols:
                dlist2.add(e[k])
            for e in dlist2:
                dlist.append([e, 'h1i', i*algo.int_size, "h2i", i*algo.int_size])
            print(dlist)
            differential.append(('not', hash_framework.models.vars.choice_differentials(dlist)))
        else:
            differential.append(models.vars.differential(cols[0][k], 'h1i', i*algo.int_size, "h2i", i*algo.int_size))

    hash_framework.models.vars.write_clause('cdifferentials', tuple(differential), "07-differential.txt")


def exists_unit_step(algo, start, target, tag="md4-wangs-sasakis-connected"):
    pos = hash_framework.attacks.collision.metric.loose.delta(algo, start, target)
    r = []
    i = 0
    for e in pos:
        m = hash_framework.models()
        m.start(tag, False)
        hash_framework.models.vars.write_header()
        if i == 0:
            hash_framework.models.generate(algo, ['h1', 'h2'])

        i += 1
        hash_framework.attacks.collision.connected.loose.constraints(algo, start, e)
        hash_framework.attacks.collision.write_constraints(algo)
        hash_framework.attacks.collision.write_optional_differential(algo)
        hash_framework.models.vars.write_values(algo.default_state_bits, 'h1s', "01-h1-state.txt")
        hash_framework.models.vars.write_values(algo.default_state_bits, 'h2s', "01-h2-state.txt")
        hash_framework.models.vars.write_assign(['ccollision', 'cblocks', 'cdifferentials'])
        m.collapse()
        m.build()
        sat = m.run(count=1)
        if not sat:
            continue

        rs = m.results(algo)
        r.extend(rs)
        #attacks.collision.insert_db_multiple(algo, db, rs, tag)
    return r

def all_neighbors(algo, db, start, tag):
    cols = [start.copy()]
    hash_framework.attacks.collision.insert_db_multiple(algo, db, cols, tag + "-original")
    for i in range(0, 48):
        j = 0
        while True:
            m = hash_framework.models()
            m.start(tag+"-r" + str(i), False)
            hash_framework.models.vars.write_header()

            if j == 0:
                hash_framework.models.generate(algo, ['h1', 'h2'])

            hash_framework.attacks.collision.connected.loose.constraints_new_neighbor(algo, cols, i)
            hash_framework.attacks.collision.write_constraints(algo)
            hash_framework.attacks.collision.write_optional_differential(algo)
            hash_framework.models.vars.write_values(algo.default_state_bits, 'h1s', "01-h1-state.txt")
            hash_framework.models.vars.write_values(algo.default_state_bits, 'h2s', "01-h2-state.txt")
            hash_framework.models.vars.write_assign(['ccollision', 'cblocks', 'cdifferentials'])
            m.collapse()
            m.build()
            sat = m.run(count=1)
            if not sat:
                break
            rs = m.results(algo)
            ncols = hash_framework.attacks.collision.build_col_rows(algo, db, rs, tag)
            cols.extend(ncols)
            hash_framework.attacks.collision.insert_db_multiple(algo, db, rs, tag)
            j += 1

    #attacks.collision.insert_db_multiple(algo, db, cols[1:], tag)
    return cols

def parallel_all_neighbors(algo, db, start, tag):
    cols = [start.copy()]
    hash_framework.attacks.collision.insert_db_multiple(algo, db, cols, tag + "-original")
    wq = []
    for i in range(0, 48):
        wq.append((i))

    jq = []

    while len(wq) > 0:
        print(wq)
        i = wq.pop(0)

        m = hash_framework.models()
        m.start(tag+"-r" + str(i), False)
        hash_framework.models.vars.write_header()
        hash_framework.models.generate(algo, ['h1', 'h2'])
        hash_framework.attacks.collision.connected.loose.constraints_new_neighbor(algo, cols, i)
        hash_framework.attacks.collision.write_constraints(algo)
        hash_framework.attacks.collision.write_optional_differential(algo)
        hash_framework.models.vars.write_values(algo.default_state_bits, 'h1s', "01-h1-state.txt")
        hash_framework.models.vars.write_values(algo.default_state_bits, 'h2s', "01-h2-state.txt")
        hash_framework.models.vars.write_assign(['ccollision', 'cblocks', 'cdifferentials'])
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
                        m = hash_framework.models()
                        m.start(tag + "-r" + str(jqr), False)
                        rs = m.results(algo)
                        ncols = hash_framework.attacks.collision.build_col_rows(algo, db, rs, tag)
                        cols.extend(ncols)
                        wq.append(jqr)
                    jq.remove(jq[j])
                    break

    hash_framework.attacks.collision.insert_db_multiple(algo, db, cols[1:], tag)
    return cols

def parallel_find_path(algo, db, start, target, tag):
    cols = [start.copy()]
    min_distance = hash_framework.attacks.collision.metric.loose.distance(algo, start, target)

    hash_framework.attacks.collision.insert_db_multiple(algo, db, cols, tag + "-original")
    wqs = {}
    wqs[0] = []
    wcols = {}
    wcols[0] = [start]
    wdist = {}
    wdist[0] = [min_distance]
    for i in range(0, 48):
        wqs[0].append((i))
    working_cols = [0]

    jq = []
    while len(working_cols) > 0 and min_distance > 0:
        print("min_distance: " + str(min_distance))
        print("working_cols: " + str(working_cols))
        wc = working_cols.pop(0)
        print("wc: " + str(wc))
        print("wqs[wc]: " + str(wqs[wc]))
        i = wqs[wc].pop(0)
        print("i: " + str(i))
        if len(wqs[wc]) > 0:
            working_cols.append(wc)

        found = False
        for j in range(0, len(jq)):
            if jq[j][0] == wc and jq[j][1] == i:
                found = True
                break
        if found:
            wqs[wc].append(i)
            if wc not in working_cols:
                working_cols.append(wc)
            continue


        m = hash_framework.models()
        m.start(tag + "-c" + str(wc) + "-r" + str(i), False)
        hash_framework.models.vars.write_header()
        hash_framework.models.generate(algo, ['h1', 'h2'])
        hash_framework.attacks.collision.connected.loose.constraints_new_neighbor(algo, wcols[wc], i)
        hash_framework.attacks.collision.write_constraints(algo)
        hash_framework.attacks.collision.write_optional_differential(algo)
        hash_framework.models.vars.write_assign(['ccollision', 'cblocks', 'cdifferentials'])
        m.collapse()
        m.build()
        jqj = compute.perform_sat("problem.cnf", "problem.out", count=1, no_wait=True, ident=(wc, i))
        jq.append((wc, i, jqj))

        while compute.assign_work() is None or (len(working_cols) == 0 and len(jq) > 0):
            print("Waiting for work...")
            fj = compute.wait_job_hosts(loop_until_found=True)
            fj_status = fj[0]
            fj_job = fj[1]
            fj_ident = fj_job[6]
            for j in range(0, len(jq)):
                jqe = jq[j]
                jqwc = jqe[0]
                jqi = jqe[1]
                jqj = jqe[2]
                if fj_ident[0] == jqwc and fj_ident[1] == jqi:
                    print("Found finished job:")
                    print((fj, jqe))
                    if fj_status:
                        m = hash_framework.models()
                        m.start(tag + "-c" + str(jqwc) + "-r" + str(jqi), False)
                        rs = m.results(algo)
                        ncols = hash_framework.attacks.collision.build_col_rows(algo, db, rs, tag)
                        if len(ncols) < 1:
                            continue
                        ncol = ncols[0]
                        hash_framework.attacks.collision.insert_db_multiple(algo, db, ncols, tag)

                        # Check if min_distance needs updating
                        ndist = hash_framework.attacks.collision.metric.loose.distance(algo, ncol, target)

                        # Only add if not already in cols
                        nci = -1
                        dte = list(map(lambda x: hash_framework.attacks.collision.metric.loose.distance(algo, ncol, x), cols))
                        if 0 not in dte:
                            nci = len(cols)
                            cols.append(ncol)
                            wcols[nci] = []
                            wdist[nci] = []
                            wqs[nci] = list(range(0, 48))
                            wcols[nci].append(ncol)
                            wdist[nci].append(ndist)
                        else:
                            nci = dte.index(0)

                        if jqwc not in working_cols:
                            working_cols.append(jqwc)

                        # Add to every other class of distance 1
                        for i in range(0, len(dte)):
                            if dte[i] == 1:
                                wcols[i].append(ncol)
                                wdist[i].append(ndist)
                                dr = hash_framework.attacks.collision.metric.loose.delta(algo, cols[i], cols[nci])
                                if dr[0][0] not in wqs[i]:
                                    wqs[i].append(dr[0][0])

                                if i not in working_cols and wdist[i][0] <= min_distance:
                                    working_cols.append(i)

                                wcols[nci].append(cols[i])
                                wdist[nci].append(wdist[i][0])
                                if dr[0][0] not in wqs[nci]:
                                    wqs[nci].append(dr[0][0])

                        # Check if min_dist needs updating
                        # If so, add it to wq
                        if ndist <= min_distance:
                            print("Updating min_distance: " + str(min_distance) + " - " + str(ndist))
                            min_distance = ndist
                            working_cols.append(nci)

                        offset = 0
                        working_cols = []
                        while len(working_cols) == 0 and offset < 4:
                            for i in range(0, len(cols)):
                                if hash_framework.attacks.collision.metric.loose.distance(algo, target, cols[i]) <= (min_distance+offset) and len(wqs[i]) > 0:
                                    working_cols.append(i)
                            offset += 1

                    jq.remove(jq[j])
                    break

    hash_framework.attacks.collision.insert_db_multiple(algo, db, cols, tag)
    return cols

def parallel_find_path_hybrid(algo, db, start, target, tag):
    cols = [start.copy()]
    min_distance = hash_framework.attacks.collision.metric.loose.distance(algo, start, target)

    hash_framework.attacks.collision.insert_db_multiple(algo, db, cols, tag + "-original")
    wqs = {}
    wqs[0] = [-1] + list(range(0, 48))
    wcols = {}
    wcols[0] = [cols[0]]
    wdist = {}
    wdist[0] = [min_distance]
    working_cols = []
    unit_cols = [0]

    new_found = 0
    repeat_found = 0

    jq = []
    while (len(working_cols) > 0 or len(unit_cols) > 0) and min_distance > 1:
        print("min_distance: " + str(min_distance))
        print("discovered vertices: " + str(len(cols)))
        print("unit_cols: " + str(unit_cols))
        print("working_cols: " + str(working_cols))
        print("job_queue: " + str(list(map(lambda x: (x[0], x[1]), jq))))
        print("ratio: " + str(new_found) + " : " + str(repeat_found))
        override = False
        if len(unit_cols) > 0:
            wc = unit_cols.pop()
            i = -1
            found = False
            for j in range(0, len(jq)):
                if jq[j][0] == wc and jq[j][1] == i:
                    found = True
                    break
            if found:
                override = True

            print(len(wcols[wc]))

            m = hash_framework.models()
            m.start(tag + "-c" + str(wc) + "-r" + str(i), False)
            hash_framework.models.vars.write_header()
            hash_framework.models.generate(algo, ['h1', 'h2'])
            hash_framework.attacks.collision.connected.loose.new_unit_step(algo, wcols[wc][0], wcols[wc], target)
            hash_framework.attacks.collision.write_constraints(algo)
            hash_framework.attacks.collision.write_optional_differential(algo)
            hash_framework.models.vars.write_assign(['ccollision', 'cblocks', 'cdifferentials'])
            m.collapse()
            m.build()
            jqj = compute.perform_sat("problem.cnf", "problem.out", count=1, no_wait=True, ident=(wc, i))
            jq.append((wc, i, jqj))
            wqs[wc].remove(-1)
        else:
            wc = working_cols.pop(0)
            print("wc: " + str(wc))
            print("wqs[wc]: " + str(wqs[wc]))
            i = wqs[wc].pop(0)
            print("i: " + str(i))
            if len(wqs[wc]) > 0:
                working_cols.append(wc)

            found = False
            for j in range(0, len(jq)):
                if jq[j][0] == wc and jq[j][1] == i:
                    found = True
                    break
            if found:
                if wc not in working_cols and len(wqs[wc]) > 0:
                    working_cols.append(wc)
                override = True
            else:
                m = hash_framework.models()
                m.start(tag + "-c" + str(wc) + "-r" + str(i), False)
                hash_framework.models.vars.write_header()
                hash_framework.models.generate(algo, ['h1', 'h2'])
                hash_framework.attacks.collision.connected.loose.constraints_new_neighbor(algo, wcols[wc], i)
                hash_framework.attacks.collision.write_constraints(algo)
                hash_framework.attacks.collision.write_optional_differential(algo)
                hash_framework.models.vars.write_assign(['ccollision', 'cblocks', 'cdifferentials'])
                m.collapse()
                m.build()
                jqj = compute.perform_sat("problem.cnf", "problem.out", count=1, no_wait=True, ident=(wc, i))
                jq.append((wc, i, jqj))

        while override or compute.assign_work() is None or (len(working_cols) == 0 and len(unit_cols) == 0 and len(jq) > 0):
            override = False
            print("Waiting for work...")
            fj = compute.wait_job_hosts(loop_until_found=True)
            fj_status = fj[0]
            fj_job = fj[1]
            fj_ident = fj_job[6]
            for j in range(0, len(jq)):
                jqe = jq[j]
                jqwc = jqe[0]
                jqi = jqe[1]
                jqj = jqe[2]
                if fj_ident[0] == jqwc and fj_ident[1] == jqi:
                    print("Found finished job:")
                    print((fj, jqe))
                    if fj_status:
                        m = hash_framework.models()
                        m.start(tag + "-c" + str(jqwc) + "-r" + str(jqi), False)
                        rs = m.results(algo)
                        ncols = hash_framework.attacks.collision.build_col_rows(algo, db, rs, tag)
                        if len(ncols) < 1:
                            continue
                        ncol = ncols[0]
                        hash_framework.attacks.collision.insert_db_multiple(algo, db, ncols, tag)

                        # Check if min_distance needs updating
                        ndist = hash_framework.attacks.collision.metric.loose.distance(algo, ncol, target)

                        # Only add if not already in cols
                        nci = -1
                        dte = list(map(lambda x: hash_framework.attacks.collision.metric.loose.distance(algo, ncol, x), cols))
                        if 0 not in dte:
                            nci = len(cols)
                            cols.append(ncol)
                            wcols[nci] = [ncol]
                            wqs[nci] = [-1] + list(range(0, 48))
                            wdist[nci] = [ndist]
                            new_found += 1
                        else:
                            nci = dte.index(0)
                            repeat_found += 1


                        if jqi == -1 and -1 not in wqs[jqwc]:
                            wqs[jqwc] = [-1] + wqs[jqwc]

                        # Add to every other class of distance 1
                        for i in range(0, len(dte)):
                            if dte[i] == 1 and i in wqs:
                                wcols[i].append(ncol)
                                wdist[i].append(ndist)
                                dr = hash_framework.attacks.collision.metric.loose.delta(algo, cols[i], cols[nci])
                                if dr[0][0] not in wqs[i]:
                                    wqs[i].append(dr[0][0])

                                wcols[nci].append(cols[i])
                                wdist[nci].append(wdist[i][0])

                                if dr[0][0] not in wqs[nci]:
                                    wqs[nci].append(dr[0][0])

                        # Check if min_dist needs updating
                        # If so, add it to wq
                        if ndist <= min_distance:
                            print("Updating min_distance: " + str(min_distance) + " - " + str(ndist))
                            min_distance = ndist

                    elif jqi == -1:
                            if -1 in wqs[jqwc]:
                                jqwc.remove(-1)

                            for i in range(0, len(cols)):
                                if hash_framework.attacks.collision.metric.loose.distance(algo, cols[i], cols[jqwc]) == 1:
                                    wcols[jqwc].append(cols[i])
                                    wdist[jqwc].append(wdist[i][0])
                                    if cols[jqwc] not in wcols[i]:
                                        wcols[i].append(cols[jqwc])
                                        wdist[i].append(ndist)
                            working_cols.append(jqwc)

                    jq.remove(jq[j])

                    # Recompute unit_cols after updating
                    unit_cols = []
                    offset = 0
                    while len(unit_cols) == 0 and offset < 1:
                        for i in range(0, len(cols)):
                            if hash_framework.attacks.collision.metric.loose.distance(algo, target, cols[i]) <= (min_distance+offset) and -1 in wqs[i]:
                                found = False
                                for job in jq:
                                    if job[0] == i:
                                        found = True
                                        break
                                if not found and i not in unit_cols:
                                    unit_cols = [i] + unit_cols
                        offset += 1

                    if fj_status and jqi == -1 and jqwc not in unit_cols:
                        unit_cols = [jqwc] + unit_cols

                    # Recompute working_cols after updating
                    offset = 0
                    working_cols = []
                    while len(working_cols) == 0 and offset < 3:
                        for i in range(0, len(cols)):
                            if hash_framework.attacks.collision.metric.loose.distance(algo, target, cols[i]) <= (min_distance+offset) and -1 not in wqs[i] and len(wqs[i]) > 0:
                                working_cols = [i] + working_cols
                        offset += 1

                    break

    hash_framework.attacks.collision.insert_db_multiple(algo, db, cols, tag)
    return cols
