import hash_framework
import datetime, time, sys, json

def run():
    jq = []
    c = hash_framework.manager.api.Client(hash_framework.config.master_uri)
    c.register()
    while True:
        jq, error = c.receive_jobs(hash_framework.config.job_count)
        if error != None:
            print("[receive_jobs] Error: " + str(error))
            time.sleep(1)
            continue

        print(jq)

        r = []
        for jid in jq:
            ji, error = c.get_job(jid)
            if error != None:
                print("[get_job] Error: " + str(error))
                continue

            print(ji)

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
