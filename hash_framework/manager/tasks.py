import hash_framework.config as config
import hash_framework

import datetime

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
            return False

        for data in datas:
            if type(data) != dict:
                return False
            if 'name' not in data or type(data['name']) != str:
                return False
            if 'algo' not in data or type(data['algo']) != str:
                return False

            keys = set(data)
            all_keys = {'max_threads', 'priority', 'running', 'name', 'algo'}

            if len(keys.difference(all_keys)) != 0:
                return False

            if 'max_threads' in data and type(data['max_threads']) != int:
                return False
            if 'priority' in data and type(data['priority']) != int:
                return False
            if 'running' in data and type(data['priority']) != bool:
                return False

        return True

    def add_all(self, datas):
        default_priority = 100
        default_threads = -1
        default_running = False
        current_time = datetime.datetime.now()

        for i in range(len(datas)):
            if 'max_threads' not in datas[i]:
                datas[i]['max_threads'] = default_threads

            if 'priority' not in datas[i]:
                datas[i]['priority'] = default_priority

            if 'running' not in datas[i]:
                datas[i]['running'] = default_running

            datas[i] = (datas[i]['name'], datas[i]['algo'],
                        datas[i]['max_threads'], datas[i]['priority'],
                        current_time, datas[i]['running'])

        q = "INSERT INTO tasks (name, algo, max_threads, priority, started, running) VALUES %s"

        r = self.db.prepared_many(q, datas, commit=True, limit=1, cursor=True)
        return r

class Task:
    def __init__(self, db):
        self.db = db

        self.id = None
        self.name = None
        self.algo = None
        self.max_threads = None
        self.priority = None
        self.running = None

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'algo': self.algo,
                'max_threads': self.max_threads, 'priority': self.priority,
                'running': self.running}

    def new(self, name, algo, max_threads=-1, priority=100, running=False):
        assert(type(name) == str)
        assert(type(algo) == str)
        assert(type(max_threads) == int)
        assert(type(priority) == int)
        assert(type(running) == bool)

        self.name = name
        self.algo = algo
        self.max_threads = max_threads
        self.priority = priority
        self.running = running

        self.__insert__()

        return self

    def load_id(self, tid):
        assert(type(tid) == int)
        self.id = tid

        self.__load__()
        return self

    def load(self, name):
        assert(type(name) == str)
        self.name = name

        self.__load__()

        return self

    def remove(self):
        self.__remove__()

        return self

    def get_jobs(self):
        results = []

        q = "SELECT job_id FROM assigns WHERE task_id=%s"

        r, cur = self.db.prepared(q, [self.id], cursor=True)

        data = cur.fetchall()
        for d in data:
            results.append(d[0])

        return results

    def __insert__(self):
        q = "INSERT INTO tasks"
        q += " (name, algo, max_threads, priority, started, running)"
        q += " VALUES (%s, %s, %s, %s, now(), %s)"
        q += " RETURNING id;"
        values = (self.name, self.algo, self.max_threads, self.priority, self.running)

        r, rid = self.db.prepared(q, values, rowid=True)
        self.id = rid


    def __load__(self):
        q = ""
        values = tuple()

        if self.name != None:
            q = "SELECT id, algo, max_threads, priority, running"
            q += " FROM tasks WHERE name=%s;"
            values = tuple([self.name])
        elif self.id != None:
            q = "SELECT name, algo, max_threads, priority, running"
            q += " FROM tasks WHERE id=%s;"
            values = tuple([self.id])

        r, cursor = self.db.prepared(q, values, commit=False, cursor=True)

        data = cursor.fetchone()
        if data:
            self.id = data[0]
            self.algo = data[1]
            self.max_threads = int(data[2])
            self.priority = int(data[3])
            self.running = bool(data[4])
        else:
            self.id = None
            self.name = None
            self.algo = None
            self.max_threads = None
            self.priority = None
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
