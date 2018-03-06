import sys

from flask import Flask
from flask import request
from flask import jsonify
from flask import send_from_directory

import hash_framework
from hash_framework import config

# config.port = int(sys.argv[1])

app = Flask(__name__, static_url_path='', static_folder='../../static')

db_pool = []
next_task_obj = {}

def acquire_db():
    if len(db_pool) == 0:
        db = hash_framework.database()
        db.close()
        db.init_psql()
        db_pool.append(db)
        return db

    return db_pool[0]

    # return db_pool[0]

def release_db(db):
    #db.close()
    #db.init_psql()
    pass

def fill_task_obj(db):
    if 'sent_jobs' in next_task_obj:
        q = "UPDATE jobs SET state=%s, owner=%s WHERE id=%s"
        for t in next_task_obj['sent_jobs']:
            db.prepared(q, [1, t[0], t[1]], commit=False)

    if 'ordered_tasks' in next_task_obj:
        q = "UPDATE tasks SET remaining_jobs=(remaining_jobs-%s),current_threads=(current_threads+%s) WHERE id=%s"
        for task in next_task_obj['ordered_tasks']:
            db.prepared(q, [task['remaining_jobs_delta'], task['current_threads_delta'], task['id']], commit=True)

    next_task_obj['jobs'] = {}
    next_task_obj['sent_jobs'] = set()
    next_task_obj['ordered_tasks'] = []

    jobs = {}

    t = hash_framework.manager.Tasks(db)
    ots = t.get_task_objects_by_priority()
    for task in ots:
        jobs[task['id']] = t.get_task_free_jobs(tid=task['id'], limit=10000)

    next_task_obj['jobs'] = jobs
    next_task_obj['sent_jobs'] = set()
    next_task_obj['ordered_tasks'] = ots
    next_task_obj['regen'] = False

def pop_tasks(db, host_id, limit=1):
    if 'regen' not in next_task_obj or next_task_obj['regen']:
        print("Regen")
        fill_task_obj(db)

    jobs = next_task_obj['jobs']
    jids = []
    tids = set()
    for task in next_task_obj['ordered_tasks']:
        remaining_threads = (task['current_threads'] < task['max_threads'] or
                             task['max_threads'] == -1)
        remaining_jobs = task['remaining_jobs']

        if remaining_threads and remaining_jobs:
            while len(jids) < limit and len(jobs[task['id']]) > 0:
                jid = jobs[task['id']][0]
                jobs[task['id']] = jobs[task['id']][1:]
                next_task_obj['sent_jobs'].add((host_id, jid))
                jids.append(jid)
                task['remaining_jobs'] -= 1
                if 'remaining_jobs_delta' not in task:
                    task['remaining_jobs_delta'] = 0

                task['remaining_jobs_delta'] += 1

                if len(jobs[task['id']]) == 0 and task['remaining_jobs'] > 0:
                    next_task_obj['regen'] = True

            if task['id'] not in tids:
                tids.add(task['id'])
                task['current_threads'] += 1

                if 'current_threads_delta' not in task:
                    task['current_threads_delta'] = 0

                task['current_threads_delta'] += 1

        if len(jids) == limit:
            break

    return jids

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/index.html')
def index():
    return app.send_static_file('index.html')

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
            return jsonify(hash_framework.manager.input_error), 400

        if t.add_all(datas) != None:
            release_db(db)
            return jsonify(hash_framework.manager.success)

        release_db(db)
        return jsonify(hash_framework.manager.server_error), 500

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
            return jsonify(hash_framework.manager.input_error), 400

        if j.add_all(datas) != None:
            release_db(db)
            return jsonify(hash_framework.manager.success)

        release_db(db)
        return jsonify(hash_framework.manager.server_error), 500
    elif request.method == 'GET':
        t = hash_framework.manager.Task(db)
        r = t.load_id(tid).get_jobs()
        release_db(db)
        return jsonify(r)

@app.route("/job/<int:jid>", methods=['GET', 'POST'])
def handle_task_job(jid):
    db = acquire_db()
    j = hash_framework.manager.Job(db)
    if request.method == 'POST':
        release_db(db)
        pass
    elif request.method == 'GET':
        j.load(jid)
        r = j.to_dict()
        release_db(db)
        return jsonify(r)

@app.route("/job/<int:jid>/update_status", methods=['POST'])
def handle_task_job_update_status(jid):
    db = acquire_db()
    if request.method == 'POST':
        pass
    release_db(db)

#@app.route("/task/<int:tid>/job/<int:jid>/", methods=['GET', 'POST'])
#def handle_task_job(tid, jid):
#    db = acquire_db()
#    if request.method == 'POST':
#        pass
#    elif request.method == 'GET':
#        pass

@app.route("/ip/", methods=['GET'])
def handle_ip_request():
    if 'REMOTE_ADDR' in request.headers:
        return request.headers['REMOTE_ADDR']
    elif 'HTTP_X_FORWARDED_FOR' in request.headers:
        return request.headers['HTTP_X_FORWARDED_FOR']

    return request.remote_addr

@app.route("/hosts/", methods=['GET', 'POST'])
def handle_hosts():
    db = acquire_db()
    h = hash_framework.manager.Hosts(db)
    if request.method == 'POST':
        datas = request.get_json(force=True)
        if type(datas) != dict or not h.verify([datas]):
            release_db(db)
            return jsonify(hash_framework.manager.input_error), 400

        h = hash_framework.manager.Host(db)
        h.new(datas['ip'], datas['hostname'], datas['cores'], datas['memory'],
              datas['disk'], datas['version'], datas['in_use'])

        if h.id == None:
            release_db(db)
            return jsonify(hash_framework.manager.server_error), 500
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
    return jsonify(hash_framework.manager.success)

@app.route("/host/<int:hid>/metadata", methods=['GET', 'POST'])
def handle_host_metadata(hid):
    db = acquire_db()
    h = hash_framework.manager.Host(db)

    if request.method == 'POST':
        datas = request.get_json(force=True)
        if type(datas) != dict or len(datas) != 2 or 'name' not in datas or 'value' not in datas:
            release_db(db)
            return jsonify(hash_framework.manager.input_error), 400

        h.load_id(hid).add_metadata(datas['name'], datas['value'])
        release_db(db)
        return jsonify(hash_framework.manager.success)
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

@app.route("/host/<int:hid>/assign/", methods=['GET'])
def handle_assign(hid):
    db = acquire_db()
    r = pop_tasks(db, hid, 1)
    release_db(db)
    return jsonify(r)

@app.route("/host/<int:hid>/assign/<int:count>", methods=['GET'])
def handle_multi_assign(hid, count):
    db = acquire_db()
    r = pop_tasks(db, hid, count)
    release_db(db)
    return jsonify(r)

@app.route("/results/", methods=['POST'])
def handle_results():
    db = acquire_db()

    if request.method == 'POST':
        j = hash_framework.manager.Jobs(db)
        if not j.verify_results(datas):
            release_db(db)
            return jsonify(hash_framework.manager.input_error), 400

        if j.add_results(datas) != True:
            return jsonify(hash_framework.manager.server_error), 500

        return jsonify(hash_framework.manager.success)

@app.route("/update/", methods=['GET'])
def handle_update():
    db = acquire_db()
    t = hash_framework.manager.Tasks(db)
    t.update_all_job_counts()
    next_task_obj['regen'] = True
    fill_task_obj(db)
    release_db(db)
    return jsonify(hash_framework.manager.success)

if __name__ == "__main__":
    app.run()
