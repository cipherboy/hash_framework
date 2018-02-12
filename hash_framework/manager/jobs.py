import hash_framework.config as config
import hash_framework

class Jobs:
    def __init__(self, db):
        self.db = db

    def load_ids(self):
        results = []

        q = "SELECT id FROM jobs;"

        r, cur = self.db.execute(q, cursor=True)

        data = cur.fetchall()
        for d in data:
            results.append(d[0])

        return results

    def verify(self, datas):
        if type(datas) != list:
            return False

        for data in datas:
            if type(data) != dict:
                return False

            if 'task' not in data or type(data['task']) != int:
                return False
            if 'kernel' not in data or type(data['kernel']) != str:
                return False
            if 'algo' not in data or type(data['algo']) != str:
                return False
            if 'args' not in data or type(data['args']) != str:
                return False
            if 'result_table' not in data or type(data['result_table']) != str:
                return False

        return True

    def add_all(self, datas):
        tids = set()
        for i in range(0, len(datas)):
            tids.add(datas[i]['task'])
            datas[i] = (datas[i]['task'], datas[i]['kernel'], datas[i]['algo'],
                        datas[i]['args'], datas[i]['result_table'], 0)

        q = "INSERT INTO jobs (task_id, kernel, algo, args, result_table, state) VALUES %s"

        r = self.db.prepared_many(q, datas, commit=True, limit=1, cursor=True)

        t = hash_framework.manager.Task(self.db)
        for tid in tids:
            t.update_job_counts(tid)

        return r

class Job:
    def __init__(self, db):
        self.db = db

        self.id = None
        self.task = None
        self.owner = None

        self.kernel = None
        self.algo = None
        self.args = None
        self.result_table = None

        self.start_time = None
        self.compile_time = None
        self.compile_return = None
        self.run_time = None
        self.run_return = None
        self.finalize_time = None
        self.checked_back = None

    def new(self, task, kernel, algo, args, result_table):
        self.task = task
        self.kernel = kernel
        self.algo = algo
        self.args = args
        self.result_table = result_table

        self.__insert__()

        return self

    def load(self, jid):
        assert(type(jid) == int)
        self.name = name

        self.__load__()

        return self

    def __insert__(self):
        q = "INSERT INTO jobs"
        q += " (task_id, kernel, algo, args, result_table, state)"
        q += " VALUES (%s, %s, %s, %s, %s, 0)"
        q += " RETURNING id;"
        values = (self.task_id, self.kernel, self.algo, self.args,
                  self.result_table)

        r, rid = self.db.prepared(q, values, rowid=True)
        self.id = rid

        t = hash_framework.manager.Task(self.db)
        t.update_job_counts(self.task_id)

    def __load__(self):
        q = "SELECT task_id, kernel, algo, args, result_table, state,"
        q += " start_time, compile_time, compile_return, run_time,"
        q += " run_return, finalize_time, checked_back"
        q += " FROM jobs WHERE id=%s;"
        values = tuple([self.id])

        r, cursor = self.db.prepared(q, values, commit=False, cursor=True)

        data = cursor.fetchone()
        if data:
            self.task_id = int(data[0])
            self.kernel = data[1]
            self.algo = data[2]
            self.args = data[3]
            self.result_table = data[4]
            self.state = data[5]
            self.start_time = data[6]
            self.compile_time = data[7]
            self.compile_return = data[8]
            self.run_time = data[9]
            self.run_return = data[10]
            self.finalize_time = data[11]
            self.checked_back = data[12]
        else:
            self.id = None
            self.task_id = None
            self.kernel = None
            self.algo = None
            self.args = None
            self.result_table = None
            self.start_time = None
            self.compile_time = None
            self.compile_return = None
            self.run_time = None
            self.run_return = None
            self.finalize_time = None
            self.checked_back = None

        cursor.close()
