import time, time
import base64, json
import subprocess, sys, random
import gc

from flask import Flask
from flask import request

import hash_framework
import hash_framework.workers.worker as worker

if len(sys.argv) >= 2:
    hash_framework.config.manager_uri = sys.argv[1]

if len(sys.argv) >= 3:
    hash_framework.config.scheduler_uri = sys.argv[2]

if len(sys.argv) == 4 and sys.argv[3] == 'debug':
    worker.debug()
elif len(sys.argv) >= 5 and sys.argv[3] == 'debug':
    jid = int(sys.argv[4])
    worker.debug(jid)
else:
    worker.run()
