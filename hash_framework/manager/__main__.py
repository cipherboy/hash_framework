import sys

from flask import Flask
from flask import request
from flask import jsonify

import hash_framework
from hash_framework import config

# config.port = int(sys.argv[1])

app = Flask(__name__)

db_pool = []

def acquire_db():
    if len(db_pool) == 0:
        db = hash_framework.database()
        db.close()
        db.init_psql()
        db_pool.append(db)
        print("Created worker")
        return db

    return db_pool[0]

def release_db(db):
    pass

@app.route("/tasks/", methods=['GET', 'POST'])
def handle_tasks():
    db = acquire_db()
    t = hash_framework.manager.Tasks(db)
    if request.method == 'POST':
        datas = request.get_json(force=True)
        if type(datas) == dict:
            datas = [datas]

        if not t.verify(datas):
            release_db(db)
            return "Invalid input data", 400

        if t.add_all(datas) != None:
            release_db(db)
            return "OK", 200

        release_db(db)
        return "Internal Error", 500

    elif request.method == 'GET':
        r = t.load_ids()
        release_db(db)
        return jsonify(r)

@app.route("/task/<int:tid>/", methods=['GET'])
def handle_task(tid):
    db = acquire_db()
    t = hash_framework.manager.Task(db)
    r = t.load_id(tid)
    release_db(db)
    return jsonify(r.to_dict())

@app.route("/task/<int:tid>/jobs/", methods=['GET', 'POST'])
def handle_task_jobs(tid):
    db = acquire_db()
    if request.method == 'POST':
        j = hash_framework.manager.Jobs(db)
        datas = request.get_json(force=True)
        if type(datas) == dict:
            datas = [datas]

        if not j.verify(datas):
            release_db(db)
            return "Invalid input data", 400

        if t.add_all(datas) != None:
            release_db(db)
            return "OK", 200

        release_db(db)
        return "Internal Error", 500
    elif request.method == 'GET':
        t = hash_framework.manager.Task(db)
        r = t.load_id(tid).get_jobs()
        release_db(db)
        return jsonify(r)

@app.route("/task/<int:tid>/job/<int:jid>", methods=['GET', 'POST'])
def handle_task_job(tid, jid):
    db = acquire_db()
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        pass

@app.route("/hosts/", methods=['GET', 'POST'])
def handle_hosts():
    db = acquire_db()
    h = hash_framework.manager.Hosts(db)
    if request.method == 'POST':
        datas = request.get_json(force=True)
        if type(datas) != dict or not h.verify([datas]):
            release_db(db)
            return "Invalid input data", 400

        h = hash_framework.manager.Host(db)
        h.new(datas['ip'], datas['hostname'], datas['cores'], datas['memory'],
              datas['disk'], datas['version'], datas['in_use'])

        if h.id == None:
            release_db(db)
            return "Internal Error", 500
        else:
            release_db(db)
            return jsonify(h.id)
    elif request.method == 'GET':
        r = h.load_ids()
        release_db(db)
        return jsonify(r)

@app.route("/host/<int:hid>", methods=['GET'])
def handle_host(hid):
    db = acquire_db()
    h = hash_framework.manager.Host(db)
    r = h.load_id(hid)
    release_db(db)
    return jsonify(r.to_dict())

@app.route("/host/<int:hid>/heartbeat", methods=['GET'])
def handle_host_heartbeat(hid):
    db = acquire_db()
    h = hash_framework.manager.Host(db)
    h.load_id(hid).heartbeat()
    release_db(db)
    return "OK"

@app.route("/host/<int:hid>/metadata", methods=['GET', 'POST'])
def handle_host_metadata(hid):
    db = acquire_db()
    h = hash_framework.manager.Host(db)

    if request.method == 'POST':
        datas = request.get_json(force=True)
        if type(datas) != dict or len(datas) != 2 or 'name' not in datas or 'value' not in datas:
            release_db(db)
            return "Invalid input data", 400

        h.load_id(hid).add_metadata(datas['name'], datas['value'])
        release_db(db)
        return "OK"
    elif request.method == 'GET':
        r = h.load_id(hid).metadata_keys()
        release_db(db)
        return jsonify(r)

@app.route("/host/<int:hid>/metadata/<string:name>", methods=['GET'])
def handle_host_metadata_query(hid, name):
    db = acquire_db()
    h = hash_framework.manager.Host(db)

    if request.method == 'GET':
        value = h.load_id(hid).get_metadata(name)
        release_db(db)
        r = {'host_id': hid, 'name': name, 'value': value}
        return jsonify(r)

@app.route("/assign/", methods=['GET', 'POST'])
def handle_assign():
    db = acquire_db()
    t = hash_framework.manager.Tasks(db)
    r = t.assign_next_job()
    release_db(db)
    return jsonify(r)

if __name__ == "__main__":
    app.run()
