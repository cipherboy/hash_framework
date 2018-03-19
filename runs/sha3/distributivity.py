import hash_framework as hf
import json

def __main__():
    manager_uri = 'http://127.0.0.1:8000'
    scheduler_uri = 'http://127.0.0.1:8001'
    c = hf.manager.api.Client(manager_uri, scheduler_uri)
    tid = c.create_task('sha3-distributivity-zzz', 'sha3', running=True, priority=10)
    # tid = 34
    print("Task ID: " + str(tid))

    kernel_name = "sha3distributivity"
    kernel = hf.kernels.lookup(kernel_name)
    algo = "sha3"
    ws = [1, 2, 4, 8, 16, 32, 64]
    rounds = []
    for i in range(1, 25):
        r = ['t', 'r', 'p', 'c'] * i
        rounds.append(r)
    work = kernel.gen_work(rounds, ws)

    jobs = []
    for obj in work:
        args = json.dumps(obj)
        obj = {'task': tid, 'algo': algo, 'kernel': kernel_name, 'args': args,
               'result_table': "c_" + algo}
        jobs.append(obj)

        if len(jobs) > 10000:
            c.create_jobs(tid, jobs)
            jobs = []

    if len(jobs) > 0:
        c.create_jobs(tid, jobs)


__main__()
