import hash_framework.config as config
import hash_framework

class Task:
    def __init__(self, db):
        self.db = db

        self.id = None
        self.name = None
        self.algo = None
        self.max_threads = None
        self.priority = None

    def new(self, name, algo, max_threads=-1, priority=100):
        assert(type(name) == str)
        assert(type(algo) == str)
        assert(type(max_threads) == int)
        assert(type(priority) == int)

        self.name = name
        self.algo = algo
        self.max_threads = max_threads
        self.priority = priority

        self.__insert__()

        return self

    def load(self, name):
        assert(type(name) == str)
        self.name = name

        self.__load__()

        return self

    def remove(self):
        self.__remove__()

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
