import sqlite3
import time, sys

from hash_framework.config import config

class database:
    def __init__(self, path=None):
        if path == None:
            path = config.results_dir + "/framework_results.db"
        print(path)
        self.path = path
        self.conn = sqlite3.connect(path)

    def execute(self, q, commit=True, limit=20, rowid=False):
        for i in range(0, limit):
            try:
                c = self.conn.cursor()
                r = c.execute(q)
                if commit or rowid:
                    print((commit, rowid))
                    self.conn.commit()
                if rowid:
                    return r, c.lastrowid
                return r
            except Exception as e:
                if i < limit-1:
                    time.sleep(1)
                print("Database Error:", file=sys.stderr)
                print(e, file=sys.stderr)
                pass

        return None

    def commit(self):
        self.conn.commit()

    def query(self, table, cols, rowid=0, tag="", limit=0):
        assert(type(table) == str)
        assert(type(cols) == list and len(cols) > 0)
        assert(type(rowid) == int)
        assert(type(tag) == str)
        assert(type(limit) == int)
        q = "SELECT " + ','.join(cols) + " FROM " + table
        if rowid > 0:
            q += " WHERE ROWID=" + str(rowid)
        elif tag != "":
            q += " WHERE tag='" + tag + "'"
        if limit > 0:
            q += " LIMIT " + str(limit)
        q += ";"
        c = self.conn.cursor()
        c.execute(q)
        raw_datas = c.fetchall()
        data = []
        for raw_data in raw_datas:
            assert(len(raw_data) == len(cols))
            d = {}
            for i in range(0, len(cols)):
                d[cols[i]] = raw_data[i]
            data.append(d)
        if limit == 1:
            data = data[0]
        return data
