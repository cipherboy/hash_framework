import hash_framework
import datetime, time, sys, json


def run():
    data = []

    c = hash_framework.manager.api.Client(
        hash_framework.config.manager_uri, hash_framework.config.scheduler_uri
    )
    c.register()

    while True:
        jq, error = c.receive_jobs(hash_framework.config.job_count)
        if error != None:
            print("[receive_jobs] Error: " + str(error))
            time.sleep(10)

        if len(jq) == 0:
            break

        r = []
        for jid in jq:
            ji, error = c.get_job(jid)
            if error != None:
                print("[get_job] Error: " + str(error))
                continue

            kernel_name = ji["kernel"]
            kernel_args = json.loads(ji["args"])
            c_count = len(kernel_args["rounds"]) // 4
            w = kernel_args["w"]
            j = hash_framework.workers.Job(
                jid, kernel_name, kernel_args, ji["timeout"], datetime.datetime.now()
            )

            j.run()
            result = j.to_dict(datetime.datetime.now())
            data.append((c_count, w, result["run_return"]))
            print(data)
            # r.append(result)

    print(data)

    # error = c.send_results(r)
    # if error != None:
    #     print("[send_results] Error: " + str(error))


if len(sys.argv) >= 2:
    hash_framework.config.manager_uri = sys.argv[1]

if len(sys.argv) >= 3:
    hash_framework.config.scheduler_uri = sys.argv[2]

run()
