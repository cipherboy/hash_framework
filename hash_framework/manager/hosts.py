import hash_framework.config as config
import hash_framework

class Hosts:
    def __init__(self, db):
        self.db = db

    def load_ids(self):
        results = []

        q = "SELECT id FROM hosts;"

        r, cur = self.db.execute(q, cursor=True)

        data = cur.fetchall()
        for d in data:
            results.append(d[0])

        return results

    def verify(self, datas):
        if type(datas) != list:
            return False

        for data in datas:
            if 'ip' not in data or type(data['ip']) != str:
                return False
            if 'hostname' not in data or type(data['hostname']) != str:
                return False
            if 'cores' not in data or type(data['cores']) != int:
                return False
            if 'memory' not in data or type(data['memory']) != int:
                return False
            if 'disk' not in data or type(data['disk']) != int:
                return False
            if 'version' not in data or type(data['version']) != str:
                return False
            if 'in_use' not in data or type(data['in_use']) != bool:
                return False

        return True

class Host:
    def __init__(self, db):
        self.db = db

        self.id = None

        self.ip = None
        self.hostname = None

        self.cores = None
        self.memory = None
        self.disk = None

        self.registered = None
        self.last_seen = None

        self.version = None
        self.in_use = None

    def to_dict(self):
        return {'ip': self.ip, 'hostname': self.hostname, 'cores': self.cores,
                'memory': self.memory, 'disk': self.disk,
                'registered': self.registered, 'last_seen': self.last_seen,
                'version': self.version, 'in_use': self.in_use}

    def new(self, ip, hostname, cores, memory, disk, version, in_use):
        assert(type(ip) == str)
        assert(type(hostname) == str)
        assert(type(cores) == int)
        assert(type(memory) == int)
        assert(type(disk) == int)
        assert(type(version) == str)
        assert(type(in_use) == bool)

        self.ip = ip
        self.hostname = hostname
        self.cores = cores
        self.memory = memory
        self.disk = disk
        self.version = version
        self.in_use = in_use

        self.__insert__()

        return self

    def load_id(self, hid):
        assert(type(hid) == int)

        self.id = hid

        self.__load__()
        return self

    def load(self, ip, hostname):
        assert(type(ip) == str)
        assert(type(hostname) == str)

        self.ip = ip
        self.hostname = hostname

        self.__load__()

        return self

    def metadata_keys(self):
        q = "SELECT name FROM host_metadata WHERE host_id=%s"
        r, c = self.db.prepared(q, [self.id], cursor=True)
        datas = c.fetchall()

        keys = []
        for data in datas:
            keys.append(data[0])

        return keys

    def add_metadata(self, name, value):
        assert(type(name) == str)
        assert(type(value) == str)

        try:
            q = "DELETE FROM host_metadata WHERE host_id=%s AND name=%s"
            self.db.prepared(q, (self.id, name))
        except:
            pass

        q = "INSERT INTO host_metadata (host_id, name, value) VALUES (%s, %s, %s)"
        self.db.prepared(q, (self.id, name, value))

    def get_metadata(self, name):
        q = "SELECT value FROM host_metadata WHERE host_id=%s AND name=%s"
        r, c = self.db.prepared(q, (self.id, name), cursor=True)
        value = c.fetchone()
        if value is not None:
            value = value[0]

        c.close()
        return value

    def heartbeat(self):
        if self.id == None:
            return

        q = "UPDATE hosts SET last_seen=now() WHERE id=%s"
        self.db.prepared(q, [self.id], commit=True)

        return

    def remove(self):
        self.__remove__()

        return self

    def __insert__(self):
        q = "INSERT INTO hosts"
        q += " (ip, hostname, cores, memory, disk, registered, last_seen, version, in_use)"
        q += " VALUES (%s, %s, %s, %s, %s, now(), now(), %s, %s)"
        q += " RETURNING id;"
        values = (self.ip, self.hostname, self.cores, self.memory, self.disk, self.version, self.in_use)

        r, rid = self.db.prepared(q, values, rowid=True)
        self.id = rid

    def __load__(self):
        q = "SELECT id, ip, hostname, cores, memory, disk, registered,"
        q += " last_seen, version, in_use FROM hosts WHERE"
        values = []

        if self.id != None:
            q += " id=%s"
            values = [self.id]
        elif self.ip != None and self.hostname != None:
            q += " ip=%s AND hostname=%s"
            values = [self.ip, self.hostname]

        r, cursor = self.db.prepared(q, values, commit=False, cursor=True)

        data = cursor.fetchone()
        if data:
            self.id = data[0]
            self.ip = data[1]
            self.hostname = data[2]
            self.cores = int(data[3])
            self.memory = int(data[4])
            self.disk = int(data[5])
            self.registered = data[6]
            self.last_seen = data[7]
            self.version = data[8]
            self.in_use = bool(data[9])
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

        if self.id != None:
            q = "DELETE FROM host_metadata WHERE host_id=%s;"
            values = [self.id]
            r = self.db.prepared(q, values, commit=True)
            q = "DELETE FROM hosts WHERE host_id=%s;"
            r = self.db.prepared(q, values, commit=True)
