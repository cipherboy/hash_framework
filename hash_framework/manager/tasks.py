import hash_framework.config as config
import hash_framework

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
            all_keys = {'max_threads', 'priority', 'name', 'algo'}

            if len(keys.difference(all_keys)) != 0:
                return False

            if 'max_threads' in data and type(data['max_threads']) != int:
                return False
            if 'priority' in data and type(data['priority']) != int:
                return False

        return True

    def add_all(self, datas):
        default_priority = 100
        default_threads = -1

        for i in range(len(datas)):
            if 'max_threads' not in datas[i]:
                datas[i]['max_threads'] = default_threads

            if 'priority' not in datas[i]:
                datas[i]['priority'] = default_priority

            datas[i] = (datas[i]['name'], datas[i]['algo'],
                        datas[i]['max_threads'], datas[i]['priority'])

        q = "INSERT INTO tasks (name, algo, max_threads, priority) VALUES %s"

        self.db.prepared_many(q, datas, commit=True)

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
