import requests

class Client:
    def __init__(self, uri):
        self.uri = uri

    def register(self):
        pass

    def heartbeat(self):
        pass

    def receive_jobs(self, count=1):
        assert(type(count) == int and count > 0)
        r = requests.get(self.uri + "/assign/" + str(count))

        if r.status_code == 200:
            return r.json(), {}

        return [], r.json()

    def start_job(self, tid, jid):
        pass

    def end_job(self, tid, jid):
        pass

    def send_results(self, results):
        r = request.post(self.uri + "/results/", json=results)

        if r.status_code == 200:
            return True, {}

        return False, r.json()
