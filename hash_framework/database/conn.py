import sqlite3
import psycopg2
import psycopg2.extras
import time
import sys

from hash_framework.config import Config


class Database:
    def __init__(self, path=None):
        if path is None:
            path = Config.results_dir + "/framework_results.db"

        self.type = "sqlite3"
        self.path = path
        self.conn = sqlite3.connect(self.path)

    def init_psql(self, database=None, host=None, user=None, password=None):
        database = database if database is not None else Config.psql_database
        host = host if host is not None else Config.psql_host
        user = user if user is not None else Config.psql_user
        password = password if password is not None else Config.psql_password

        self.type = "psql"
        self.conn = psycopg2.connect(
            host=host, user=user, password=password, database=database
        )

    def to_type(self, col_type, binary=False):
        if col_type.startswith('hex'):
            # Use a TEXT field of size |bits (if specified after the type
            # identifier). Encode and decode to/from hex, transparently
            # returning an integer to the caller.
            if self.type == "sqlite3":
                # sqlite3 doesn't enforce varchar lengths
                return 'TEXT'
            # Postgres enforces widths; handle the optional bits specifier
            width = 0
            if '|' in col_type:
                p_index = col_type.index('|')
                width = int(col_type[p_index+1:])

                if not binary:
                    assert (width % 4) == 0
                    width = width//4

            if width == 0:
                return 'TEXT'
            return 'CHAR(' + str(width) + ')'
        assert False

    def sqlite_rowid(self, r, c, cursor):
        lastrowid = c.lastrowid

        if cursor:
            return r, lastrowid, c
        else:
            c.close()
            return r, lastrowid

    def psql_rowid(self, r, c, cursor):
        tmp = c.fetchone()
        lastrowid = 0
        if tmp is not None and len(tmp) == 1:
            lastrowid = tmp[0]

        if cursor:
            return r, lastrowid, c
        else:
            c.close()
            return r, lastrowid

    def rowid(self, r, c, rowid, cursor):
        if rowid:
            if self.type == "psql":
                return self.psql_rowid(r, c, cursor)
            else:
                return self.sqlite3_rowid(r, c, cursor)

        if cursor:
            return r, c
        else:
            c.close()
            return r

    def execute(self, q, commit=True, limit=20, rowid=False, cursor=False):
        for i in range(0, limit):
            c = None
            try:
                c = self.conn.cursor()
                r = c.execute(q)
                if commit or rowid:
                    self.conn.commit()

                return self.rowid(r, c, rowid, cursor)
            except Exception as e:
                if c:
                    c.close()
                    c = None

                print("Database Error (" + self.type + "):", file=sys.stderr)
                print(e, file=sys.stderr)

                if i < limit - 1:
                    time.sleep(1)
                self.conn.rollback()
                pass
            if c:
                c.close()
        return None

    def prepared(self, q, values, commit=True, limit=20, rowid=False, cursor=False):
        for i in range(0, limit):
            c = None
            try:
                c = self.conn.cursor()
                r = c.execute(q, values)
                if commit or rowid:
                    self.conn.commit()

                return self.rowid(r, c, rowid, cursor)
            except Exception as e:
                if c:
                    c.close()
                    c = None

                print("Database Error (" + self.type + "):", file=sys.stderr)
                print(e, file=sys.stderr)

                if i < limit - 1:
                    time.sleep(1)

                self.conn.rollback()
                pass

            if c:
                c.close()

        return None

    def prepared_many(self, q, values_list, commit=True, limit=20, cursor=False):
        for i in range(0, limit):
            c = None
            try:
                c = self.conn.cursor()
                r = psycopg2.extras.execute_values(c, q, values_list)

                if commit:
                    self.conn.commit()

                return self.rowid(r, c, False, cursor)
            except Exception as e:
                if c:
                    c.close()
                    c = None

                print("Database Error (" + self.type + "):", file=sys.stderr)
                print(e, file=sys.stderr)

                if i < limit - 1:
                    time.sleep(1)

                self.conn.rollback()
                pass

        if c:
            c.close()

        return None

    def query(self, table, cols, rowid=0, tag="", limit=0):
        assert type(table) == str
        assert type(cols) == list and len(cols) > 0
        assert type(rowid) == int
        assert type(tag) == str
        assert type(limit) == int

        q = "SELECT " + ",".join(cols) + " FROM " + table
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
            assert len(raw_data) == len(cols)
            d = {}
            for i in range(0, len(cols)):
                d[cols[i]] = raw_data[i]
            data.append(d)

        if limit == 1:
            data = data[0]

        return data

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()
