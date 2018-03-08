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
    c.register()
    count = 0
    rtime = 0
    rc = 0
    gtime = 0
    gc = 0
    utime = 0
    uc = 0
    stime = 0
    sc = 0
    while True:
        t1 = time.time()
        jq, error = c.receive_jobs(hash_framework.config.job_count)
        if error != None:
            print("[receive_jobs] Error: " + str(error))
            time.sleep(10)
            continue

        if jq == []:
            print("[receive_jobs] No Jobs")
            time.sleep(10)
            continue
        rtime += time.time() - t1
        rc += 1

        r = []
        for jid in jq:
            print(jid)
            t1 = time.time()
            ji, error = c.get_job(jid)
            if error != None:
                print("[get_job] Error: " + str(error))
                continue
            gtime += time.time() - t1
            gc += 1
            print(ji)

            t1 = time.time()
            kernel_name = ji['kernel']
            kernel_args = json.loads(ji['args'])

            j = hash_framework.workers.Job(jid, kernel_name, kernel_args,
                                           ji['timeout'],
                                           datetime.datetime.now())

            j.run()
            r.append(j.to_dict(datetime.datetime.now()))
            j.clean()
            utime += time.time() - t1
            uc += 1

            error = c.end_job(ji['task_id'], jid)
            if error != None:
                print("[end_job] Ignoring Error: " + str(error))

        t1 = time.time()
        for i in range(1, 10):
            error = c.send_results(r)
            if error != None:
                print("[send_results] Error: " + str(error))
                time.sleep(1)
                if i == 9:
                    print("Dumping results and quitting:")
                    print(r)
                    sys.exit(1)
            else:
                break

        stime += time.time() - t1
        sc += 1

        if (sc % 100) == 0:
            print(((rtime/rc), (gtime/gc), (utime/uc), (stime/sc)))
