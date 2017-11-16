import itertools


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

def generate_reduced_test_delta(d, n, r):
    if n >= len(d):
        return [()]

    return list(itertools.combinations(d, len(d) - n))


"""class Extended(Loom):
    def __init__(self, algo, db, start_state, start_block, rounds, delta_set, min_delta, max_delta, tag_base):
        self.algo = algo
        self.db = db
        self.start_state = start_state
        self.start_block = start_block
        self.rounds = rounds
        self.delta_set = delta_set
        self.min_delta = min_delta
        self.max_delta = max_delta
        self.tag_base = tag_base
        self.sat = []
        super().__init__()

    def start(self):
        for r in self.rounds:
            m = models()
            tag = self.tag_base + "-r" + str(r)
            m.start(tag, False)
            models.vars.write_header()
            models.generate(self.algo, ['h1', 'h2'], rounds=r, bypass=True)
            models.vars.write_values(self.start_state, 'h1s', "01-h1-state.txt")
            models.vars.write_values(self.start_state, 'h2s', "01-h2-state.txt")
            models.vars.write_values(self.start_block, 'h1b', "15-h1-state.txt")
            attacks.collision.write_constraints(self.algo)
            attacks.collision.write_optional_differential(self.algo)
            models.vars.write_assign(['ccollision', 'cblocks', 'cstate', 'cdifferentials', 'cnegated'])
            m.collapse(bc="00-combined-model.txt")

    def gen_work(self):
        work = set()

        for r in self.rounds:
            for delta in self.delta_set:
                for n in range(self.min_delta, self.max_delta+1):
                    for e in attacks.collision.reduced.generate_test_delta(delta, n, r - 4):
                        work.add((type(self.algo), r, len(e), e, self.tag_base))

        print("gen_work(): " + str(len(work)))
        return list(work)

    def pre_run(data):
        algo_type, r, s, e, tag_base = data

        algo = algo_type()
        algo.rounds = r

        m = models()
        tag = tag_base + "-r" + str(r) + "-s" + str(s) + "-e" + '-'.join(list(map(str, e)))

        m.start(tag, False)
        os.system("ln -s " + m.model_dir + "/" + tag_base + "-r" + str(r) + "/00-combined-model.txt " + m.model_dir + "/" + tag + "/00-combined-model.txt")
        attacks.collision.reduced.specified_difference(algo, e)
        m.collapse()
        m.build()

        return m.model_dir + "/" + tag + "/problem.cnf"

    def run_sat(self, path, data, raw=None):
        algo_type, r, s, e, tag_base = data
        self.sat.append((r, s, e))
        print((r, s, e))

def fabric_extended(algo, db, start_state, start_block, rounds, delta_set, min_delta, max_delta, tag_base):
    loom = attacks.collision.second_preimage.Extended(algo, db, start_state, start_block, rounds, delta_set, min_delta, max_delta, tag_base)
    fabric.set_loom(loom)
    fabric.spin_from_object(cmsfabric_config)
    fabric.run()
    print(loom.sat)

def find_extended(algo, db, start_state, start_block, delta_set, rounds, tag_base):
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
    models.vars.write_values(start_state, 'h1s', "01-h1-state.txt")
    models.vars.write_values(start_state, 'h2s', "01-h2-state.txt")
    models.vars.write_values(start_block, 'h1b', "15-h1-state.txt")
    attacks.collision.write_constraints(algo)
    attacks.collision.write_optional_differential(algo)
    models.vars.write_assign(['ccollision', 'cblocks', 'cstate', 'cdifferentials', 'cnegated'])

    print("Generating work queue...")
    for deltas in delta_set:
        for n in range(2, 3):
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
"""
