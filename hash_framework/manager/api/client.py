import requests

class Client:
    def __init__(self, uri):
        self.uri = uri

    def register(self):
        self._heartbeat()
        pass

    def _heartbeat(self):
        pass

    def receive_jobs(self, count=1):
        assert(type(count) == int and count > 0)
        self._heartbeat()
        r = requests.get(self.uri + "/assign/" + str(count))

        if r.status_code == 200:
            return r.json(), {}

        return [], r.json()

    def get_job(self, jid):
        self._heartbeat()
        pass

    def end_job(self, tid, jid):
        self._heartbeat()
        pass

    def send_results(self, results):
        self._heartbeat()
        r = request.post(self.uri + "/results/", json=results)

        if r.status_code == 200:
            return True, {}

        return False, r.json()
