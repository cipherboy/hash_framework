import hash_framework as hf
import json


def get_cw():
    db = hf.database()
    db.close()
    db.init_psql()

    results = []

    mjid = 36791300
    tid = 82
    q = (
        "SELECT run_return, args FROM jobs WHERE task_id="
        + str(tid)
        + " AND state=2 AND id >= "
        + str(mjid)
        + ";"
    )
    r, cur = db.execute(q, cursor=True)

    last_round = ["r", "p", "c", "i22", "t", "r", "p", "c", "i23"]

    row = cur.fetchone()
    while row != None:
        run_return, args = row
        obj = json.loads(args)
        rounds = obj["rounds"]
        diff = obj["differences"]

        if run_return == 10 and rounds == last_round:
            results.append((rounds, diff))

        row = cur.fetchone()

    print(len(results))

    return results


def __main__():
    manager_uri = "http://127.0.0.1:8000"
    scheduler_uri = "http://127.0.0.1:8001"
    c = hf.manager.api.Client(manager_uri, scheduler_uri)

    # print(get_cw())
    # return

    # tid = c.create_task('sha3-output-256', 'sha3', running=True, priority=4)
    tid = 82
    print("Task ID: " + str(tid))

    kernel_name = "sha3output"
    kernel = hf.kernels.lookup(kernel_name)
    algo = "sha3"
    work = kernel.gen_work(1, get_cw(), "t", 256)

    jobs = []
    for obj in work:
        args = json.dumps(obj)
        obj = {
            "task": tid,
            "algo": algo,
            "kernel": kernel_name,
            "args": args,
            "result_table": "c_" + algo,
        }
        jobs.append(obj)

        if len(jobs) > 10000:
            c.create_jobs(tid, jobs)
            jobs = []

    if len(jobs) > 0:
        c.create_jobs(tid, jobs)


__main__()
