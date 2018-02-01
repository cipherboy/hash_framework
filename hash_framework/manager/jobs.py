import hash_framework.config as config
import hash_framework

class Job:
    def __init__(self, db):
        self.db = db

        self.id = None
        self.task = None

        self.kernel = None
        self.algo = None
        self.args = None
        self.result_table = None

        self.start_time = None
        self.compile_time = None
        self.run_time = None
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
        q = "INSERT INTO tasks"
        q += " (name, algo, max_threads, priority, started)"
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
