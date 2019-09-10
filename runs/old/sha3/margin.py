import hash_framework as hf
import sys
import random

input_error = int(sys.argv[2])
out_error = 0
rounds = 1

w = int(sys.argv[1])
r = set()

algo = hf.algorithms.sha3(w=w, rounds=rounds)
db_path = hf.config.results_dir + "/worker_results.db"
db = hf.database(path=db_path)

sat = set()

for in_margin in range(input_error, 25 * w):
    min_v = 0
    max_v = 25 * w
    out_margin = (min_v + max_v) // 2

    searched = set()

    while min_v < max_v:
        m = hf.models()
        m.remote = False
        mn = (
            "sha3-margin-w"
            + str(w)
            + "-ie"
            + str(input_error)
            + "-im"
            + str(in_margin)
            + "-om"
            + str(out_margin)
        )
        m.start(mn, False)
        hf.models.vars.write_header()
        hf.models.generate(algo, ["h1", "h2"], bypass=True)
        hf.models.vars.write_assign(["cstart", "cinput", "coutput"])

        tail = "F" * (algo.state_size - in_margin)
        cstart = hf.models.vars.differential(tail, "h1i", in_margin, "h2i", in_margin)
        hf.models.vars.write_clause("cstart", cstart, "50-start.txt")

        tail = "*" * in_margin
        cinput = hf.models.vars.differential(tail, "h1i", 0, "h2i", 0)
        hf.models.vars.write_range_clause(
            "cinput", input_error, input_error, cinput, "50-input.txt"
        )

        tail = "*" * out_margin
        coutput = hf.models.vars.differential(tail, "h1o", 0, "h2o", 0)
        hf.models.vars.write_range_clause(
            "coutput", out_error, out_error, coutput, "50-output.txt"
        )

        m.collapse()
        m.build()
        rs = m.run(count=1)
        r.add((w, input_error, in_margin, out_margin, rs))
        searched.add(out_margin)
        if rs:
            min_v = out_margin
            sat.add(mn)
        else:
            max_v = out_margin

        old_out_margin = out_margin
        out_margin = (min_v + max_v) // 2

        if old_out_margin == out_margin or out_margin <= 0:
            break

    for out_margin in range(out_margin - 3, out_margin + 4):
        if out_margin in searched or out_margin < 0 or out_margin > 25 * w:
            continue

        m = hf.models()
        m.remote = False
        mn = (
            "sha3-margin-w"
            + str(w)
            + "-ie"
            + str(input_error)
            + "-im"
            + str(in_margin)
            + "-om"
            + str(out_margin)
        )
        m.start(mn, False)
        hf.models.vars.write_header()
        hf.models.generate(algo, ["h1", "h2"], bypass=True)
        hf.models.vars.write_assign(["cstart", "cinput", "coutput"])

        tail = "F" * (algo.state_size - in_margin)
        cstart = hf.models.vars.differential(tail, "h1i", in_margin, "h2i", in_margin)
        hf.models.vars.write_clause("cstart", cstart, "50-start.txt")

        tail = "*" * in_margin
        cinput = hf.models.vars.differential(tail, "h1i", 0, "h2i", 0)
        hf.models.vars.write_range_clause(
            "cinput", input_error, input_error, cinput, "50-input.txt"
        )

        tail = "*" * out_margin
        coutput = hf.models.vars.differential(tail, "h1o", 0, "h2o", 0)
        hf.models.vars.write_range_clause(
            "coutput", out_error, out_error, coutput, "50-output.txt"
        )

        m.collapse()
        m.build()
        rs = m.run(count=1)
        if rs:
            sat.add(mn)
        r.add((w, input_error, in_margin, out_margin, rs))

sys.stderr.write(str(list(r)))
sys.stderr.write("\n")
sys.stderr.flush()

for mn in sat:
    m.start(mn, False)
    res = m.results(algo)
    for result in res:
        col = hf.attacks.collision.build_deltas(db, algo, result)
        col["tag"] = mn
        hf.attacks.collision.insert_db_single(algo, db, col, commit=True, verify=False)
