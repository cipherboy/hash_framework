import time, time
import base64, json
import subprocess, sys, random
import gc

from flask import Flask
from flask import request

from hash_framework.workers.utils import *
from hash_framework.workers.job import Job
from hash_framework.workers.jobs import Jobs
from hash_framework.config import config

assert(len(sys.argv) == 2)

if sys.argv[1] == "db":
    import hash_framework as hf
    db_path = config.results_dir + "/worker_results.db"
    db = hf.database(path=db_path)
    for name in hf.algorithms.all_algorithms:
        algo = hf.algorithms.lookup(name)
        try:
            hf.attacks.collision.create_table(algo, db)
        except:
            pass
    sys.exit()

config.port = int(sys.argv[1])

app = Flask(__name__)

queues = Jobs(config)
queues.update_thread()

@app.route("/")
def handle_overview():
    return queues.overview()

@app.route("/ready/")
def handle_ready():
    return str(queues.ready())

@app.route("/jobs/", methods=['GET', 'POST'])
def handle_jobs():
    if request.method == 'POST':
        datas = request.get_json(force=True)
        if type(datas) == list:
            result = []
            for data in datas:
                j = Job(data['kernel_name'], data['kernel_args'])
                result.append(queues.add(j))
            return json.dumps(result)
        elif type(datas) == dict:
            j = Job(datas['kernel_name'], datas['kernel_args'])
            return queues.add(j)
        else:
            return "Invalid data", 400
    else:
        return queues.all()

@app.route("/status/<int:jid>")
def handle_status(jid):
    j = queues.get(str(jid))
    if not j:
        return "", 404

    if j.status():
        return "true", 200

    return "false", 202

@app.route("/bulk_status/", methods=['POST'])
def bulk_status():
    if request.method == 'POST':
        datas = request.get_json(force=True)
        if not type(datas) == list:
            return "Invalid data", 400

        result = {}
        for data in datas:
            j = queues.get(str(data))
            if j:
                result[data] = j.status()

        return json.dumps(result)

@app.route("/job/<int:jid>")
def handle_job(jid):
    j = queues.get(str(jid))
    if not j:
        return "", 404

    if j.status():
        return queues.result(j), 200

    return "", 202

@app.route("/bulk_job/", methods=['POST'])
def bulk_job():
    if request.method == 'POST':
        datas = request.get_json(force=True)
        if not type(datas) == list:
            return "Invalid data", 400

        result = {}
        for data in datas:
            j = queues.get(str(data))
            if j and j.status() and j.id in queues.rids:
                try:
                    result[data] = queues.result(j)
                except Exception as e:
                    print("Error processing result: " + str(e) + " " + str(data))
                    sys.stdout.flush()

        return json.dumps(result)

@app.route("/kill/<int:jid>")
def handle_kill(jid):
    j = queues.get(str(jid))
    if not j:
        return "", 404

    j.kill()
    return ""


@app.route("/clean/<int:jid>")
def handle_clean(jid):
    j = queues.get(str(jid))
    if not j:
        return "", 404

    j.clean()
    queues.jobs[jid] = None

    gc.collect()

    return ""

@app.route("/bulk_clean/", methods=['POST'])
def bulk_clean():
    if request.method == 'POST':
        datas = request.get_json(force=True)
        if not type(datas) == list:
            return "Invalid data", 400

        for data in datas:
            j = queues.get(str(data))
            if j:
                j.clean()
                queues.jobs[data] = None
        gc.collect()

        return ""


app.run(host="0.0.0.0", port=int(sys.argv[1]))
