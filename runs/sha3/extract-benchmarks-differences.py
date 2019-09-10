#!/usr/bin/env python3

import hash_framework as hf
import json, png, sys


def __main__():
    db = hf.database()
    db.close()
    db.init_psql()

    assert len(sys.argv) == 2
    tid = int(sys.argv[1])

    q = (
        "SELECT id, run_return, run_time, args FROM jobs WHERE task_id="
        + str(tid)
        + " AND state=2 AND run_time > 75000 AND run_time < 3600000 ORDER BY run_time DESC;"
    )
    r, cur = db.execute(q, cursor=True)

    row = cur.fetchone()
    while row != None:
        jid, run_return, run_time, args = row
        obj = json.loads(args)
        algo = obj["algo"]
        rounds = "-".join(obj["rounds"])
        input_error = obj["input_error"]
        output_error = obj["output_error"]
        w = obj["w"]
        # {'algo': 'sha3', 'cms_args': [], 'w': 4, 'rounds': ['p'], 'input_error': 20, 'output_error': 72}
        # print(obj)

        sat = "SAT"
        if run_return == 20:
            sat = "UNSAT"
        elif run_return != 10:
            sat = "ERROR"

        print(
            "%d %s %d %d # %s %s %d"
            % (w, rounds, input_error, output_error, algo, sat, run_time)
        )

        row = cur.fetchone()


__main__()
