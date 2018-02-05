import sys

from flask import Flask
from flask import request
from flask import jsonify

import hash_framework
from hash_framework import config

config.port = int(sys.argv[1])

app = Flask(__name__)

db = hash_framework.database()
db.close()
db.init_psql()

@app.route("/tasks/", methods=['GET', 'POST'])
def handle_tasks():
    t = hash_framework.manager.Tasks(db)
    if request.method == 'POST':
        datas = request.get_json(force=True)
        if type(datas) == dict:
            datas = [datas]

        if not t.verify(datas):
            return "Invalid input data", 400

        if t.add_all(datas) != None:
            return "OK", 200

        return "Internal Error", 500

    elif request.method == 'GET':
        return jsonify(t.load_ids())

@app.route("/hosts/", methods=['GET', 'POST'])
def handle_hosts():
    h = hash_framework.manager.Hosts(db)
    if request.method == 'POST':
        datas = request.get_json(force=True)
        if type(datas) != dict or not h.verify([datas]):
            return "Invalid input data", 400

        h = hash_framework.manager.Host(db)
        h.new(datas['ip'], datas['hostname'], datas['cores'], datas['memory'],
              datas['disk'], datas['version'], datas['in_use'])

        if h.id == None:
            return "Internal Error", 500
        else:
            return jsonify(h.id)
    elif request.method == 'GET':
        return jsonify(h.load_ids())

@app.route("/host/<int:hid>", methods=['GET'])
def handle_host(hid):
    h = hash_framework.manager.Host(db)
    return jsonify(h.load_id(hid).to_dict())

@app.route("/task/<int:tid>/", methods=['GET'])
def handle_task(tid):
    t = hash_framework.manager.Task(db)
    return jsonify(t.load_id(tid).to_dict())

@app.route("/tasks/<int:tid>/jobs/", methods=['GET', 'POST'])
def handle_task_jobs(tid):
    if request.method == 'POST':
        j = hash_framework.manager.Jobs(db)
        datas = request.get_json(force=True)
        if type(datas) == dict:
            datas = [datas]

        if not j.verify(datas):
            return "Invalid input data", 400

        if t.add_all(datas) != None:
            return "OK", 200

        return "Internal Error", 500
    elif request.method == 'GET':
        t = hash_framework.manager.Task(db)
        return jsonify(t.load_id(tid).get_jobs())

app.run(host="0.0.0.0", port=int(sys.argv[1]))
