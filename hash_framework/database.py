import sqlite3

class database:
    def __init__(self, path="framework_results.db"):
        self.path = path
        self.conn = sqlite3.connect(path)

    def execute(self, q, commit=True):
        for i in range(0, 20):
            try:
                c = self.conn.cursor()
                r = c.execute(q)
                if commit:
                    self.conn.commit()
                return r
            except Exception as e:
                time.sleep(1)
                print(e)
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
