import time, time
import base64, json
import subprocess, sys, random
import gc

from flask import Flask
from flask import request

import hash_framework
import hash_framework.workers.worker as worker

if len(sys.argv) >= 2:
    hash_framework.config.master_uri = sys.argv[1]

worker.run()
