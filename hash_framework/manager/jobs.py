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

            if 'task' not in data or type(data['task']) != int or data['task'] <= 0:
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

    def verify_results(self, datas):
        if type(datas) != list:
            print("nlist")
            return False

        for data in datas:
            if type(data) != dict:
                print("ndict")
                return False

            if 'id' not in data or type(data['id']) != int or data['id'] <= 0:
                print("nid")
                return False
            if 'results' not in data or not self.verify_result(data['results']):
                print("nresults")
                return False
            if 'checked_out' not in data or type(data['checked_out']) != str:
                print("nchecked_out")
                return False
            if 'compile_time' not in data or type(data['compile_time']) != int:
                print("ncompile_time")
                return False
            if 'compile_return' not in data or type(data['compile_return']) != int:
                print("ncompile_return")
                return False
            if 'run_time' not in data or type(data['run_time']) != int:
                print("nrun_time")
                return False
            if 'run_return' not in data or type(data['run_return']) != int:
                print("nrun_return")
                return False
            if 'finalize_time' not in data or type(data['finalize_time']) != int:
                print("nfinalize_time")
                return False
            if 'checked_back' not in data or type(data['checked_back']) != str:
                print("nchecked_back")
                return False

        return True

    def verify_result(self, results):
        if type(results) != list:
            print("nrlist")
            return False

        for result in results:
            if type(result) != dict:
                print("nrdict")
                return False

            if 'data' not in result or type(result['data']) != str:
                print("nrdata")
                return False
            if 'row' not in result or type(result['row']) != dict:
                print("nrrow")
                return False

        return True

    def add_results(self, datas):
        task_ids = set()
        # Update job state
        # Get result_table
        # Insert results into approprate result_table
        # Update results with ids.

        for data in datas:
            q = "UPDATE jobs SET checked_out=%s, compile_time=%s, compile_return=%s,"
            q += " run_time=%s, run_return=%s, finalize_time=%s, checked_back=%s,"
            q += " state=2 WHERE id=%s"
            values = [data['checked_out'], data['compile_time'], data['compile_return'],
                      data['run_time'], data['run_return'], data['finalize_time'],
                      data['checked_back'], data['id']]
            self.db.prepared(q, values, commit=False)

        for data in datas:
            q = "SELECT task_id, result_table FROM jobs WHERE id=%s"
            _, cur = self.db.prepared(q, [data['id']], cursor=True, commit=False)
            ret = cur.fetchall()
            if len(ret) != 1 and len(ret[0]) != 2:
                continue
            task_id = ret[0][0]
            result_table = ret[0][1]

            task_ids.add(task_id)

            for result in data['results']:
                columns = list(result['row'])
                values = []
                for column in columns:
                    values.append(result['row'][column])

                q = "WITH rtbid AS ("
                q += "INSERT INTO " + result_table + " ("
                q += ",".join(columns) + ") VALUES ("
                q += ",".join(["%s"] * len(columns))
                q += ") RETURNING id) "
                q += "INSERT INTO results (job_id, result_table, result_id, data)"
                q += " VALUES (%s, %s, (SELECT id FROM rtbid), %s)"
                self.db.prepared(q, values + [data['id'], result_table, result['data']], commit=False)

        for task_id in task_ids:
            q = "UPDATE tasks SET current_threads=(current_threads-1) WHERE id=%s"
            self.db.prepared(q, [task_id], commit=False)

        self.db.commit()

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
        self.owner = None
        self.task_id = None
        self.kernel = None
        self.algo = None
        self.args = None
        self.result_table = None
        self.timeout = None
        self.state = None
        self.checked_out = None
        self.compile_time = None
        self.compile_return = None
        self.run_time = None
        self.run_return = None
        self.finalize_time = None
        self.checked_back = None

    def to_dict(self):
        o = {'id': self.id, 'task_id': self.task_id, 'owner': self.owner,
             'kernel': self.kernel, 'algo': self.algo, 'args': self.args,
             'result_table': self.result_table, 'timeout': self.timeout,
             'state': self.state, 'checked_out': self.checked_out,
             'compile_time': self.compile_time,
             'compile_return': self.compile_return, 'run_time': self.run_time,
             'finalize_time': self.finalize_time, 'checked_back': self.checked_back}
        return o

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
        self.id = jid

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
        q = "SELECT task_id, owner, kernel, algo, args, result_table, timeout,"
        q += " state, checked_out, compile_time, compile_return, run_time,"
        q += " run_return, finalize_time, checked_back"
        q += " FROM jobs WHERE id=%s;"
        values = tuple([self.id])

        r, cursor = self.db.prepared(q, values, commit=False, cursor=True)

        data = cursor.fetchone()
        if data:
            self.task_id = data[0]
            self.owner = data[1]
            self.kernel = data[2]
            self.algo = data[3]
            self.args = data[4]
            self.result_table = data[5]
            self.timeout = data[6]
            self.state = data[7]
            self.checked_out = data[8]
            self.compile_time = data[9]
            self.compile_return = data[10]
            self.run_time = data[11]
            self.run_return = data[12]
            self.finalize_time = data[13]
            self.checked_back = data[14]
        else:
            self.id = None
            self.owner = None
            self.task_id = None
            self.kernel = None
            self.algo = None
            self.args = None
            self.result_table = None
            self.state = None
            self.checked_out = None
            self.compile_time = None
            self.compile_return = None
            self.run_time = None
            self.run_return = None
            self.finalize_time = None
            self.checked_back = None

        cursor.close()
