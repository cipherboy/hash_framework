import hash_framework.config as config
import hash_framework

class Result:
    def __init__(self, db):
        self.db = db

        self.job_id = None
        self.result_table = None
        self.result_id = None

    def new(self, job_id, result_table, result_id):
        self.job_id = job_id
        self.result_table = result_table
        self.result_id = result_id

        self.__insert__()

        return self

    def __insert__(self):
        q = "INSERT INTO results"
        q += " (job_id, result_table, result_id)"
        q += " VALUES (%s, %s, %s);"
        values = (self.job_id, self.result_table, self.result_id)

        r, rid = self.db.prepared(q, values, rowid=True)
        self.id = rid
