#!/usr/bin/env python3

import hash_framework as hf
import json, png, sys

def __main__():
    db = hf.database()
    db.close()
    db.init_psql()

    assert(len(sys.argv) == 2)
    tid = int(sys.argv[1])

    q = "SELECT id, run_return, run_time, args FROM jobs WHERE task_id=" + str(tid) + " AND state=2 AND run_time > 75000 ORDER BY run_time DESC;"
    r, cur = db.execute(q, cursor=True)

    row = cur.fetchone()
    while row != None:
        jid, run_return, run_time, args = row
        obj = json.loads(args)
        algo = obj['algo']
        rounds = obj['rounds']
        p = len(obj['places'])
        places = '-'.join(map(str, obj['places']))

        sat = 'SAT'
        if run_return == 20:
            sat = 'UNSAT'
        elif run_return != 10:
            sat = 'ERROR'

        print("%d %d %s # %s %s %d" % (rounds, p, places, algo, sat, run_time))

        row = cur.fetchone()


__main__()
