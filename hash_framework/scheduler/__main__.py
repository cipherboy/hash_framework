import sys, time

from flask import Flask
from flask import request
from flask import jsonify
from flask import send_from_directory

import hash_framework
from hash_framework import config

# config.port = int(sys.argv[1])

app = Flask(__name__, static_url_path='', static_folder='../../static')

success = {'status': 'success', 'status_code': 200,
           'message': 'OK'}

server_error = {'status': 'failure', 'status_code': 500,
                'message': 'Internal Server Error'}
input_error = {'status': 'failure', 'status_code': 400,
               'message': 'Supplied input data was of the wrong form'}

db_pool = []
next_task_obj = {}
stats = {}

max_cache_size = 10000

def acquire_db():
    if len(db_pool) == 0:
        db = hash_framework.database()
        db.close()
        db.init_psql()
        db_pool.append(db)
        db_pool.append(1)
        return db

    db_pool[1] = db_pool[1] + 1
    if db_pool[1] == 10000:
        db_pool = []
        db = hash_framework.database()
        db.close()
        db.init_psql()
        db_pool.append(db)
        db_pool.append(1)

    return db_pool[0]

def release_db(db):
    #db.close()
    #db.init_psql()
    pass

def fill_task_obj(db):
    if not 'fill_task' in stats:
        stats['fill_task'] = []

    t1 = time.time()
    if 'sent_jobs' in next_task_obj:
        q = "UPDATE jobs SET state=MAXIMUM(1, state), owner=%s WHERE id=%s"
        for t in next_task_obj['sent_jobs']:
            db.prepared(q, [t[0], t[1]], commit=False)

    if 'ordered_tasks' in next_task_obj:
        q = "UPDATE tasks SET remaining_jobs=(remaining_jobs-%s),current_threads=(current_threads+%s) WHERE id=%s"
        for task in next_task_obj['ordered_tasks']:
            if 'remaining_jobs_delta' in task and 'current_threads_delta' in task:
                db.prepared(q, [task['remaining_jobs_delta'], task['current_threads_delta'], task['id']], commit=True)

    next_task_obj['jobs'] = {}
    next_task_obj['sent_jobs'] = set()
    next_task_obj['ordered_tasks'] = []

    jobs = {}

    t = hash_framework.scheduler.Tasks(db)
    ots = t.get_task_objects_by_priority()
    for task in ots:
        jobs[task['id']] = t.get_task_free_jobs(tid=task['id'], limit=max_cache_size)

    job_datas = {}
    jids = []
    for tid in jobs:
        for jid in jobs[tid]:
            jids.append(jid)

    next_task_obj['jobs'] = jobs
    next_task_obj['sent_jobs'] = set()
    next_task_obj['ordered_tasks'] = ots
    next_task_obj['regen'] = False

    t2  = time.time() - t1
    stats['fill_task'].append(t2)

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

@app.route("/host/<int:hid>/assign/", methods=['GET'])
def handle_assign(hid):
    db = acquire_db()
    r = pop_tasks(db, hid, 1)
    release_db(db)
    return jsonify(r)

@app.route("/host/<int:hid>/assign/<int:count>", methods=['GET'])
def handle_multi_assign(hid, count):
    if not 'assign_count' in stats:
        stats['assign_count'] = 0

    db = acquire_db()
    r = pop_tasks(db, hid, count)
    release_db(db)
    stats['assign_count'] += 1
    return jsonify(r)

@app.route("/stats/", methods=['GET'])
def handle_stats():
    return jsonify(stats)

@app.route("/update/", methods=['GET'])
def handle_update():
    print("Handling Update")
    db = acquire_db()
    t = hash_framework.scheduler.Tasks(db)
    next_task_obj['regen'] = True
    fill_task_obj(db)
    t.update_all_job_counts()
    release_db(db)
    return jsonify(success)

if __name__ == "__main__":
    # Single threaded scheduler
    app.run(host='0.0.0.0', port='8001')
