#!/usr/bin/env python3

import hash_framework as hf
import json, png, sys


def __main__():
    db = hf.database()
    db.close()
    db.init_psql()

    assert len(sys.argv) == 2
    tid = int(sys.argv[1])

    q = "SELECT args FROM jobs WHERE task_id=" + str(tid) + ";"
    r, cur = db.execute(q, cursor=True)

    row = cur.fetchone()
    while row != None:
        args = row[0]
        obj = json.loads(args)
        rounds = obj["rounds"]
        places = obj["places"]
        print("%d %s" % (rounds, "-".join(map(str, (places)))))

        row = cur.fetchone()


__main__()
