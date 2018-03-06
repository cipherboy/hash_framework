import hash_framework
import datetime, time, sys

def run():
    jq = []
    c = hash_framework.manager.api.Client(hash_framework.config.master_uri)
    c.register()
    while True:
        jq, error = receive_jobs(hash_framework.config.job_count)
        if error != None:
            print("[receive_jobs] Error: " + str(error))
            time.sleep(1)
            continue

        r = []
        for jid in jq:
            ji, error = c.get_job(jid)
            if error != None:
                print("[get_job] Error: " + str(error))
                continue

            j = hash_framework.workers.Job(jid, ji['kernel_name'],
                                           ji['kernel_args'], ji['timeout'],
                                           datetime.datetime.now())

            j.run()
            r.append(to_dict(datetime.datetime.now()))
            j.clean()

            error = c.end_job(self, ji['task_id'], jid)
            if error != None:
                print("[end_job] Ignoring Error: " + str(error))

        for i in seq(1, 10)
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
