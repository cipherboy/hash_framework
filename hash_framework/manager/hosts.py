import hash_framework.config as config
import hash_framework

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

    def new(self, ip, hostname, cores, memory, disk, registered, last_seen, version):
        self.ip = ip
        self.hostname = hostname
        self.cores = cores
        self.memory = memory
        self.disk = disk
        self.registered = registered
        self.last_seen = last_seen
        self.version = version

        self.__insert__()

        return self

    def remove(self):
        self.__remove__()

        return self

    def __insert__(self):
        q = "INSERT INTO hosts"
        q += " (ip, hostname, cores, memory, disk, registered, last_seen, version)"
        q += " VALUES (%s, %s, %s, %s, %s, now(), now(), %s)"
        q += " RETURNING id;"
        values = (self.ip, self.hostname, self.cores, self.memory, self.disk, self.version)

        r, rid = self.db.prepared(q, values, rowid=True)
        self.id = rid

    def __remove__(self):
        q = ""
        values = []

        if self.id != None:
            q = "DELETE FROM hosts WHERE id=%s;"
            values = [self.id]

        if q != "":
            r = self.db.prepared(q, values, commit=True)
