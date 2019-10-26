import requests, json
from hash_framework.config import Config


class Client:
    def __init__(self, uri):
        self.uri = uri

    def add_sats(self, obj):
        r = requests.post(self.uri + "/jobs/", json=obj)
        if r.status_code != 200:
            return False

        jids = r.json()
        return jids

    def add_sat(self, kernel_name, kernel_args):
        obj = {"kernel_name": kernel_name, "kernel_args": kernel_args}
        r = requests.post(self.uri + "/jobs/", json=obj)
        if r.status_code != 200:
            return False

        jid = r.json()
        return jid

    def all_jobs(self):
        r = requests.get(self.uri + "/jobs/")
        if r.status_code != 200:
            return set([])

        jids = set()
        result = r.json()
        for k in result:
            for jid in result[k]:
                jids.add(jid)

        return list(jids)

    def finished(self, jid):
        r = requests.get(self.uri + "/status/" + jid)
        if r.status_code == 404:
            return None
        elif r.status_code == 200:
            return True
        return False

    def bulk_finished(self, jids):
        r = requests.post(self.uri + "/bulk_status/", json=jids)
        if r.status_code != 200:
            return {}

        return r.json()

    def result(self, jid):
        r = requests.get(self.uri + "/job/" + jid)
        if r.status_code == 404:
            return None
        elif r.status_code != 200:
            return None

        d = r.json()
        return d

    def bulk_result(self, jids):
        count = 0
        while True:
            r = requests.post(self.uri + "/bulk_job/", json=jids)
            if r.status_code != 200:
                return {}

            if count > 2:
                f = open("/tmp/error-body.txt", "wb")
                f.write(r.content)
                f.close()
                return r.json()

            try:
                res = r.json()
                return res
            except:
                pass

            count += 1

    def delete(self, jid):
        r = requests.get(self.uri + "/clean/" + jid)
        return r

    def bulk_delete(self, jids):
        r = requests.post(self.uri + "/bulk_clean/", json=jids)
        return r
