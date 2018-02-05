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
        current_time = datetime.datetime.now()

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

    def load(self, name):
        assert(type(name) == str)
        self.name = name

        self.__load__()

        return self

    def __insert__(self):
        q = "INSERT INTO jobs"
        q += " (kernel, algo, args, result_table)"
        q += " VALUES (%s, %s, %s, %s, now())"
        q += " RETURNING id;"
        values = (self.name, self.algo, self.max_threads, self.priority)

        r, rid = self.db.prepared(q, values, rowid=True)
        self.id = rid


    def __load__(self):
        q = "SELECT id, algo, max_threads, priority"
        q += " FROM tasks WHERE name=%s;"
        values = tuple([self.name])

        r, cursor = self.db.prepared(q, values, commit=False, cursor=True)

        data = cursor.fetchone()
        if data:
            self.id = data[0]
            self.algo = data[1]
            self.max_threads = int(data[2])
            self.priority = int(data[3])
        else:
            self.id = None
            self.name = None
            self.algo = None
            self.max_threads = None
            self.priority = None

        cursor.close()
