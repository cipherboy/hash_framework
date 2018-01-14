import time, time
import base64, json
import subprocess, sys, random
import threading, os.path

from hash_framework.workers.job import Job
import hash_framework as hf

class Jobs:
    def __init__(self, config):
        self.jobs = {}
        self.fj = set()
        self.jq = set()
        self.wj = set()
        self.rids = {}
        self.config = config
        self.db_path = self.config.results_dir + "/worker_results.db"
        self.db = hf.database(path=self.db_path)
        self.thread_db = None

    def update_config(self, config):
        self.config = config

    def update_thread(self):
        thread = threading.Thread(target=self.do_update)
        thread.daemon = True
        thread.start()
        return thread

    def do_update(self):
        self.thread_db = hf.database(path=self.db_path)
        while True:
            try:
                self.update()
            except Exception as e:
                print("do_update() - Thread Failure: " + str(e))
                pass
            time.sleep(0.05)


    def update(self):
        for jid in self.jq.copy():
            j = self.jobs[jid]

            if j.status() != None and jid not in self.rids:
                rids = j.finish(self.thread_db)
                self.rids[jid] = rids

            if j.status() != None:
                self.fj.add(jid)
                if jid in self.jq:
                    self.jq.remove(jid)

        while len(self.jq) < self.config.threads and len(self.wj) > 0:
            jid = self.wj.pop()
            self.jobs[jid].run()
            self.jq.add(jid)

    def overview(self):
        ps = ""
        ps += "# Status\n"
        ps += "## Overview\n\n"
        ps += " - fj: " + str(len(self.fj)) + "\n"
        ps += " - jq: " + str(len(self.jq)) + "\n"
        ps += " - wj: " + str(len(self.wj)) + "\n"

    def get(self, jid):
        if jid in self.jobs:
            return self.jobs[jid]

        return None

    def add(self, j):
        assert(type(j) == Job)
        if not j.id in self.jobs:
            self.jobs[j.id] = j
            self.wj.add(j.id)
        return j.id

    def status(self, j):
        assert(type(j) == Job)

        ps = ""
        ps += "# Job Status\n\n"
        ps += " - id: " + j.id + "\n"
        if j.rtime > 0:
            ps += " - Status: running\n"
            ps += " - Wait time: " + str(j.rtime - j.stime) + "\n"
            ps += " - Run time: " + str(time.time() - j.rtime) + "\n"
        else:
            ps += " - Status: waiting\n"
            ps += " - Wait time: " + str(time.time() - j.stime) + "\n"

        return ps

    def all(self):
        d = {"jq": list(self.jq), "wj": list(self.wj), "fj": list(self.fj)}
        return json.dumps(d)

    def result(self, j):
        assert(type(j) == Job)
        if j.status() != None and j.id not in self.rids:
            self.rids[j.id] = None
            rids = j.finish(self.db)
            self.rids[j.id] = rids

        return j.result(self.db, self.rids[j.id])

    def ready(self):
        return len(self.jq) < self.config["jobs"]
