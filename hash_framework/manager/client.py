import requests, json
from hash_framework.config import config

class Client:
    def __init__(self, uri):
        self.uri = uri

    def add_sat(self, kernel_name, kernel_args):
        obj = {'kernel_name': kernel_name, 'kernel_args': kernel_args}
        r = requests.post(self.uri + "/jobs/", json=obj)
        if r.status_code != 200:
            return False
        if int("0" + r.text) == 0:
            return False

        jid = r.text
        return jid

    def finished(self, jid):
        r = requests.get(self.uri + "/status/" + jid)
        if r.status_code == 404:
            return None
        elif r.status_code == 200:
            return True
        return False

    def result(self, jid):
        r = requests.get(self.uri + "/job/" + jid)
        if r.status_code == 404:
            return None
        elif r.status_code != 200:
            return None

        d = r.json()
        return d

    def delete(self, jid):
        r = requests.get(self.uri + "/clean/" + jid)
        return r
