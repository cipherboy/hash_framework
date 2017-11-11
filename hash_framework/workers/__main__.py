import time, time
import base64, json
import subprocess, sys, random

from flask import Flask
from flask import request

from hash_framework.workers.utils import *
from hash_framework.workers.job import Job
from hash_framework.workers.jobs import Jobs
from hash_framework.config import config

app = Flask(__name__)
queues = Jobs(config)
queues.update_thread()

@app.route("/")
def handle_overview():
    queues.update()
    return queues.overview()

@app.route("/ready/")
def handle_ready():
    queues.update()
    return str(queues.ready())

@app.route("/jobs/", methods=['GET', 'POST'])
def handle_jobs():
    if request.method == 'POST':
        data = request.get_json(force=True)
        j = Job(data['kernel_name'], data['kernel_args'])
        return queues.add(j)
    else:
        return queues.all()

@app.route("/update/")
def handle_update():
    queues.update()
    return queues.all()

@app.route("/status/<int:jid>")
def handle_status(jid):
    j = queues.get(str(jid))
    if not j:
        return "", 404

    if j.status():
        return "true", 200

    return "false", 202

@app.route("/job/<int:jid>")
def handle_job(jid):
    j = queues.get(str(jid))
    if not j:
        return "", 404

    if j.status():
        return queues.result(j), 200

    return "", 202

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
    return ""

app.run(host="0.0.0.0")
