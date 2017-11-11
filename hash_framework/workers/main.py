import time, time
import base64, json
import subprocess, sys, random

from flask import Flask
from flask import request

app = Flask(__name__)
config = json.load(open(u_c(), 'r'))
queues = Jobs(config)

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
    queues.update()
    if request.method == 'POST':
        data = request.get_data()
        print(data)
        j = Job(config)
        j.set(data)
        return queues.add(j)
    else:
        return queues.all()

@app.route("/update/")
def handle_update():
    queues.update()
    return queues.all()

@app.route("/status/<int:jid>")
def handle_status(jid):
    queues.update()
    j = queues.get(str(jid))
    if not j:
        return "", 404

    if j.status():
        return "true", 200

    return "false", 202

@app.route("/job/<int:jid>")
def handle_job(jid):
    queues.update()
    j = queues.get(str(jid))
    if not j:
        return "", 404

    if j.status():
        return queues.result(j), 200

    return "", 202


@app.route("/kill/<int:jid>")
def handle_kill(jid):
    queues.update()
    j = queues.get(str(jid))
    if not j:
        return "", 404

    j.kill()
    return ""


@app.route("/clean/<int:jid>")
def handle_clean(jid):
    queues.update()
    j = queues.get(str(jid))
    if not j:
        return "", 404

    j.clean()
    return ""
