from hash_framework.config import config
import requests, socket, psutil, subprocess

class Client:
    def __init__(self, uri):
        self.uri = uri

        r = requests.get(self.uri + "/ip/")
        self.ip = r.text
        self.hostname = socket.gethostname()
        self.cores = psutil.cpu_count()
        self.memory = psutil.virtual_memory().total
        self.disk = int(subprocess.check_output("df --block-size=1 --output=avail " + config.model_dir + " | tail -n 1", shell=True).decode('utf-8').replace("\n", ''))
        self.version = "n/a"
        self.in_use = True
        self.hid = None
        self.heartbeats = False

    def register(self):
        obj = {'ip': self.ip, 'hostname': self.hostname, 'cores': self.cores,
               'memory': self.memory, 'disk': self.disk, 'version': self.version,
               'in_use': self.in_use}

        r = requests.post(self.uri + "/hosts/", json=obj)

        if r.status_code == 200:
            self.hid = r.json()
            return None

        return r.json()

    def _heartbeat(self):
        # Heartbeats are not critical, optional
        if self.hid == None or self.heartbeats == False:
            return
        r = requests.get(self.uri + "/host/" + str(self.hid) + "/heartbeat")

    def receive_jobs(self, count=1):
        assert(type(count) == int and count > 0)
        self._heartbeat()

        r = requests.get(self.uri + "/host/" + str(self.hid) + "/assign/" + str(count))

        if r.status_code == 200:
            return r.json(), None

        return None, r.json()

    def get_job(self, jid):
        self._heartbeat()

        r = requests.get(self.uri + "/job/" + str(jid))

        if r.status_code == 200:
            return r.json(), None

        return None, r.json()

    def end_job(self, tid, jid):
        self._heartbeat()

        # TODO: Not implemented/necessary
        return None

    def send_results(self, results):
        self._heartbeat()
        r = requests.post(self.uri + "/results/", json=results)

        if r.status_code == 200:
            return None

        print(r.text)
        return r.json()
