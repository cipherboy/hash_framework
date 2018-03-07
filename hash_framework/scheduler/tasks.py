import hash_framework.config as config
import hash_framework

import datetime

class Tasks:
    def __init__(self, db):
        self.db = db

    def update_all_job_counts(self):
        t = hash_framework.manager.Task(self.db)
        for tid in self.load_ids():
            t.update_job_counts(tid)

    def get_task_objects_by_priority(self, limit=100):
        q = "SELECT id,current_threads,max_threads,total_jobs,remaining_jobs"
        q += " FROM tasks WHERE remaining_jobs > 0 AND running=true ORDER BY"
        q += " priority DESC"

        if limit != -1 and type(limit) == int and limit > 0:
            q += " LIMIT " + str(limit)

        _, cur = self.db.execute(q, cursor=True)
        r = []
        data = cur.fetchall()
        for d in data:
            o = {'id': d[0], 'current_threads': d[1],
                 'max_threads': d[2], 'total_jobs': d[3],
                 'remaining_jobs': d[4]}
            r.append(o)

        cur.close()
        return r

    def get_task_free_jobs(self, in_cur=None, tid=None, limit=100):
        if tid is None:
            return []

        q = "SELECT id FROM jobs WHERE task_id=%s AND state=0 LIMIT %s;"
        cur = in_cur

        if in_cur:
            cur.execute(q, [tid, limit])
        else:
            print([tid, limit])
            r, cur = self.db.prepared(q, [tid, limit], cursor=True)

        r = []
        data = cur.fetchall()
        for d in data:
            r.append(d[0])

        if not in_cur:
            cur.close()

        return r
