import hash_framework.config as config
import hash_framework

import datetime, sys


class Tasks:
    def __init__(self, db):
        self.db = db

    def load_ids(self):
        results = []

        q = "SELECT id FROM tasks;"

        r, cur = self.db.execute(q, cursor=True)

        data = cur.fetchall()
        for d in data:
            results.append(d[0])

        return results

    def verify(self, datas):
        if type(datas) != list:
            sys.stderr.write("rlist\n")
            return False

        for data in datas:
            if type(data) != dict:
                sys.stderr.write("rdict\n")
                return False
            if "name" not in data or type(data["name"]) != str:
                sys.stderr.write("rname\n")
                return False
            if "algo" not in data or type(data["algo"]) != str:
                sys.stderr.write("ralgo\n")
                return False

            keys = set(data)
            all_keys = {"max_threads", "priority", "running", "name", "algo"}

            if len(keys.difference(all_keys)) != 0:
                sys.stderr.write("rdiff\n")
                return False

            if "max_threads" in data and type(data["max_threads"]) != int:
                sys.stderr.write("rmax_threads\n")
                return False
            if "priority" in data and type(data["priority"]) != int:
                sys.stderr.write("rpriority\n")
                return False
            if "running" in data and type(data["running"]) != bool:
                sys.stderr.write("rrunning\n")
                return False

        return True

    def add_all(self, datas):
        default_priority = 100
        default_threads = -1
        default_running = False
        current_time = datetime.datetime.now()

        for i in range(len(datas)):
            if "max_threads" not in datas[i]:
                datas[i]["max_threads"] = default_threads

            if "priority" not in datas[i]:
                datas[i]["priority"] = default_priority

            if "running" not in datas[i]:
                datas[i]["running"] = default_running

            datas[i] = (
                datas[i]["name"],
                datas[i]["algo"],
                datas[i]["max_threads"],
                0,
                0,
                0,
                datas[i]["priority"],
                current_time,
                datas[i]["running"],
            )

        q = "INSERT INTO tasks (name, algo, max_threads, current_threads, total_jobs, remaining_jobs, priority, started, running) VALUES %s RETURNING id;"

        r = self.db.prepared_many(q, datas, commit=True, limit=1, cursor=True)
        if r == None:
            return r

        cur = r[1]
        result = []
        for e in cur.fetchall():
            result.append(e[0])

        return result

    def update_all_job_counts(self):
        t = hash_framework.manager.Task(self.db)
        for tid in self.load_ids():
            t.update_job_counts(tid)

    def get_tasks_by_priority(self, i_cur=None):
        q = "SELECT id FROM tasks WHERE remaining_jobs > 0 AND (current_threads < max_threads OR max_threads=-1) AND running=true ORDER BY priority DESC;"

        cur = i_cur

        if i_cur:
            cur.execute(q)
        else:
            _, cur = self.db.execute(q, cursor=True)

        r = []
        data = cur.fetchall()
        for d in data:
            r.append(d[0])

        if not i_cur:
            cur.close()

        return r

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
            o = {
                "id": d[0],
                "current_threads": d[1],
                "max_threads": d[2],
                "total_jobs": d[3],
                "remaining_jobs": d[4],
            }
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

    def jobs_update_state(self, cur, jids, state):
        q = "UPDATE jobs SET state=%s WHERE id=%s"
        for jid in jids:
            cur.execute(q, [state, jid])

    def tasks_update_counts(self, cur, tids):
        for tid in tids:
            q = "UPDATE tasks SET remaining_jobs=(remaining_jobs - %s) WHERE"
            q += " id=%s;"

            values = [tids[tid], tid]

            cur.execute(q, values)

    def assign_next_job(self, count=1):
        db_conn = self.db.conn
        cur = db_conn.cursor()
        cur.execute("LOCK ONLY tasks, jobs IN ACCESS EXCLUSIVE MODE")

        tids = self.get_tasks_by_priority(cur)
        if len(tids) == 0:
            db_conn.commit()
            cur.close()
            print("NO tasks")
            return []

        jids = []
        used_tids = dict()
        while len(jids) < count:
            tid = tids.pop()
            n_jids = self.get_task_free_jobs(cur, tid, count - len(jids))
            if n_jids == 0:
                continue

            jids = jids + n_jids
            if not tid in used_tids:
                used_tids[tid] = 0

            used_tids[tid] += len(n_jids)
            tids.append(tid)

        self.jobs_update_state(cur, jids, 1)
        self.tasks_update_counts(cur, used_tids)

        db_conn.commit()
        cur.close()

        return jids


class Task:
    def __init__(self, db):
        self.db = db

        self.id = None

        self.max_threads = None
        self.current_threads = None

        self.total_jobs = None
        self.remaining_jobs = None

        self.name = None
        self.algo = None

        self.priority = None

        self.started = None
        self.running = None

    def update_job_counts(self, tid):
        q = "UPDATE tasks SET total_jobs=total_jobs.count,"
        q += " remaining_jobs=remaining_jobs.count FROM"
        q += " ( SELECT COUNT(*) AS count FROM jobs WHERE task_id=%s ) AS total_jobs,"
        q += " ( SELECT COUNT(*) AS count FROM jobs WHERE task_id=%s AND state=0 )"
        q += " AS remaining_jobs WHERE id=%s;"

        values = [tid, tid, tid]

        self.db.prepared(q, values)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "algo": self.algo,
            "max_threads": self.max_threads,
            "current_threads": self.current_threads,
            "total_jobs": self.total_jobs,
            "remaining_jobs": self.remaining_jobs,
            "priority": self.priority,
            "running": self.running,
            "started": self.started,
        }

    def new(self, name, algo, max_threads=-1, priority=100, running=False):
        assert type(name) == str
        assert type(algo) == str
        assert type(max_threads) == int
        assert type(priority) == int
        assert type(running) == bool

        self.name = name
        self.algo = algo

        self.max_threads = max_threads
        self.current_threads = 0

        self.total_jobs = 0
        self.remaining_jobs = 0

        self.priority = priority

        self.running = running
        self.started = datetime.datetime.now()

        self.__insert__()

        return self

    def load_id(self, tid):
        assert type(tid) == int
        self.id = tid

        self.__load__()
        return self

    def load(self, name):
        assert type(name) == str
        self.name = name

        self.__load__()

        return self

    def remove(self):
        self.__remove__()

        return self

    def get_jobs(self):
        results = []

        q = "SELECT id FROM jobs WHERE task_id=%s"

        r, cur = self.db.prepared(q, [self.id], cursor=True)

        data = cur.fetchall()
        for d in data:
            results.append(d[0])

        return results

    def __insert__(self):
        q = "INSERT INTO tasks"
        q += " (name, algo, max_threads, current_threads, total_jobs, "
        q += " remaining_jobs, priority, started, running)"
        q += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        q += " RETURNING id;"
        values = (
            self.name,
            self.algo,
            self.max_threads,
            self.current_threads,
            self.total_jobs,
            self.remaining_jobs,
            self.priority,
            self.started,
            self.running,
        )

        r, rid = self.db.prepared(q, values, rowid=True)
        self.id = rid

    def __load__(self):
        q = ""
        values = tuple()

        q = "SELECT id, name, algo, max_threads, current_threads, total_jobs,"
        q += " remaining_jobs, priority, started, running FROM tasks"

        if self.name != None:
            q += " WHERE name=%s;"
            values = [self.name]
        elif self.id != None:
            q += " WHERE id=%s;"
            values = [self.id]

        r, cursor = self.db.prepared(q, values, commit=False, cursor=True)

        data = cursor.fetchone()
        if data:
            (
                self.id,
                self.name,
                self.algo,
                self.max_threads,
                self.current_threads,
                self.total_jobs,
                self.remaining_jobs,
                self.priority,
                self.started,
                self.running,
            ) = data
        else:
            self.id = None
            self.name = None
            self.algo = None
            self.max_threads = None
            self.current_threads = None
            self.total_jobs = None
            self.remaining_jobs = None
            self.priority = None
            self.started = None
            self.running = None

        cursor.close()

    def __remove__(self):
        q = ""
        values = []

        if self.name != None and self.id != None:
            q = "DELETE FROM tasks WHERE name=%s AND id=%s;"
            values = [self.name, self.id]
        elif self.name != None:
            q = "DELETE FROM tasks WHERE name=%s;"
            values = [self.name]
        elif self.id != None:
            q = "DELETE FROM tasks WHERE id=%s;"
            values = [self.id]

        if q != "":
            r = self.db.prepared(q, values, commit=True)
