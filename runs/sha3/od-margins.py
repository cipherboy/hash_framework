import hash_framework as hf
import json


def __main__():
    manager_uri = "http://127.0.0.1:8000"
    scheduler_uri = "http://127.0.0.1:8001"
    c = hf.manager.api.Client(manager_uri, scheduler_uri)
    tid = c.create_task("sha3-od-margin-c-trpc", "sha3", running=True, priority=3)
    # tid = 68
    print("Task ID: " + str(tid))

    kernel_name = "sha3margins"
    kernel = hf.kernels.lookup(kernel_name)
    algo = "sha3"
    for w in [1, 2, 4, 8]:
        work = kernel.gen_output_difference_margins_work(["c", "t", "r", "p", "c"], w)

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
