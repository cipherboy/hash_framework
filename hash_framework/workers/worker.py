import hash_framework
import datetime, time, sys, json

def debug():
    c = hash_framework.manager.api.Client(hash_framework.config.manager_uri, hash_framework.config.scheduler_uri)
    c.register()
    jq, error = c.receive_jobs(hash_framework.config.job_count)
    print((jq, error))
    if error != None:
        print("[receive_jobs] Error: " + str(error))
        time.sleep(10)

    r = []
    for jid in jq:
        ji, error = c.get_job(jid)
        print((jid, ji, error))
        if error != None:
            print("[get_job] Error: " + str(error))
            continue

        kernel_name = ji['kernel']
        kernel_args = json.loads(ji['args'])
        j = hash_framework.workers.Job(jid, kernel_name, kernel_args,
                                       ji['timeout'],
                                       datetime.datetime.now())

        j.run()
        result = j.to_dict(datetime.datetime.now())
        print(result)
        r.append(result)


    error = c.send_results(r)
    if error != None:
        print("[send_results] Error: " + str(error))

def run():
    jq = []
    c = hash_framework.manager.api.Client(hash_framework.config.manager_uri, hash_framework.config.scheduler_uri)
    error = True

    while error:
        try:
            c.register()
            error = False
        except Exception as e:
            error = True
            print("[register] Error: " + str(e))
            time.sleep(10)

    while True:
        try:
            jq, error = c.receive_jobs(hash_framework.config.job_count)
        except Exception as e:
            error = "exception: " + str(e)

        if error != None:
            print("[receive_jobs] Error: " + str(error))
            time.sleep(10)
            continue

        if jq == []:
            print("[receive_jobs] No Jobs")
            time.sleep(10)
            continue

        print("[receiving jobs]: " + str(len(jq)) + " jobs")
        r = []
        for jid in jq:
            ji, error = c.get_job(jid)
            if error != None:
                print("[get_job] Error: " + str(error))
                continue

            kernel_name = ji['kernel']
            kernel_args = json.loads(ji['args'])

            j = hash_framework.workers.Job(jid, kernel_name, kernel_args,
                                           ji['timeout'],
                                           datetime.datetime.now())

            j.run()
            r.append(j.to_dict(datetime.datetime.now()))
            j.clean()

            error = c.end_job(ji['task_id'], jid)
            if error != None:
                print("[end_job] Ignoring Error: " + str(error))

        for i in range(1, 10):
            try:
                error = c.send_results(r)
            except Exception as e:
                error = "exception: " + str(e)

            if error != None:
                print("[send_results] Error: " + str(error))
                time.sleep(1)
                if i == 9:
                    print("Manually dumping results and quitting:")
                    print(r)
                    sys.exit(1)
            else:
                break
