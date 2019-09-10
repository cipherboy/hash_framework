import hash_framework as hf
import json


def __main__():
    manager_uri = "http://127.0.0.1:8000"
    scheduler_uri = "http://127.0.0.1:8001"
    c = hf.manager.api.Client(manager_uri, scheduler_uri)
    tid = c.create_task("sha3-id-margin-trpci0-t", "sha3", running=True, priority=4)
    # tid = 61
    print("Task ID: " + str(tid))

    kernel_name = "sha3margins"
    kernel = hf.kernels.lookup(kernel_name)
    algo = "sha3"
    for w in [1, 2, 4]:
        work = kernel.gen_input_difference_margins_work(
            ["t", "r", "p", "c", "i0", "t"], w, [128, 160, 224, 256, 384, 512]
        )

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
