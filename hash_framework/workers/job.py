import time, os, shutil
import base64, json
import subprocess, sys, random

from hash_framework.workers.utils import *
from hash_framework.config import config
import hash_framework.kernels as kernels

class Job:
    def __init__(self, kernel_name, kernel_args):
        # Copy config
        self.id = u_ri()
        self.kernel_type = kernels.lookup(kernel_name)
        self.kernel = self.kernel_type(self.id, kernel_args)

        self.of = None
        self._p = None

        self.stime = time.time()
        self.rtime = 0
        self.ftime = 0

    def run(self):
        self.kernel.pre_run()
        cmd = self.kernel.run_cmd()
        out_path = self.kernel.out_path()

        self.of = open(out_path, 'w')
        self._p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=self.of, shell=True)
        self.rtime = time.time()

    def status(self):
        if self._p != None and self._p.poll() != None:
            if self.of != None and not self.of.closed:
                self.of.flush()
                self.of.close()
            if self.ftime == 0:
                self.ftime = time.time()
            return self._p.returncode
        return None

    def kill(self):
        if self._p != None and self._p.poll() == None:
            self._p.kill()
            self._p.terminate()
        if self.of != None and not self.of.closed:
            self.of.flush()
            self.of.close()
        if self.ftime == 0:
            self.ftime = time.time()

    def result(self):
        return {"id": self.id, "return": self.status(), "results": self.kernel.post_run(self.status())}

    def clean(self):
        self.kernel.clean()
