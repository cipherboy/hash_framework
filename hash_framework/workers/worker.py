import hash_framework
import datetime

def __worker__():
    jq = []
    c = hash_framework.manager.api.Client(hash_framework.config.master_uri)
    c.register()
    while True:
        jq = receive_jobs(1)
        r = []
        for jid in jq:
            ji = c.get_job(jid)
            j = hash_framework.workers.Job(jid, ji['kernel_name'],
                                           ji['kernel_args'], ji['timeout'],
                                           datetime.datetime.now())
            j.run()
            r.append(to_dict(datetime.datetime.now()))
            j.clean()
            c.end_job(self, ji['task_id'], jid)
        c.send_results(r)
