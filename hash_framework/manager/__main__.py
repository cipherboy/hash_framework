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

        t.add(datas)
        return "OK"

    elif request.method == 'GET':
        return jsonify(t.load_ids())


app.run(host="0.0.0.0", port=int(sys.argv[1]))
