import time, os, shutil
import base64, json
import subprocess, sys, random

from hash_framework.workers.utils import *
from hash_framework.config import config
import hash_framework.kernels as kernels
from multiprocessing import Process

class Job:
    def __init__(self, jid, kernel_name, kernel_args, timeout, checked_out):
        # Copy config
        self.id = jid
        self.kernel_type = kernels.lookup(kernel_name)
        self.kernel_args = kernel_args
        self.kernel = None

        self.timeout = timeout
        self.checked_out = checked_out
        self.compile_time = -1
        self.compile_return = -1
        self.run_time = -1
        self.run_return = -1
        self.finalize_time = -1
        self.checked_back = ""
        self.data = ""

        self.of = None
        self._p = None

    def run(self):
        if self.kernel == None:
            self.kernel = self.kernel_type(self.id, self.kernel_args)

        # pre_run == compile_time
        # Includes building shared module (if not available), building
        # specific module, and compiling module
        self.compile_time   = time.time()
        self.compile_return = self.kernel.pre_run()
        self.compile_time   = (time.time() - self.compile_time)

        # Get run command from the kernel
        cmd = self.kernel.run_cmd()
        out_path = self.kernel.out_path()
        self.of = open(out_path, 'w')

        self.run_time = time.time()
        self._p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                                   stdout=self.of, shell=True)

        # Timeout cleanup
        if timeout <= 0:
            timeout = None

        # Wait for job to finish
        try:
            self.run_return = self._p.wait(timeout=self.timeout)
        except:
            self.run_return = -2

            # Ensure on error that process gets fully terminated.
            try:
                self._p.kill()
                self._p.terminate()
            except:
                pass

            print("Job timed out (" + str(self.timeout) + "s) - jid:" + str(self.id))

        # Close output file descriptor
        if not self.of.closed:
            self.of.flush()
            self.of.close()
            self.of = None

        self._p = None
        self.run_time = (time.time() - self.run_time)

    def to_dict(self, checked_back):
        obj = {}

        self.finalize_time = time.time()
        results = self.kernel.post_run(self.run_return)
        self.finalize_time = (time.time() - self.finalize_time)

        obj['id'] = self.id
        obj['checked_out'] = self.checked_out
        obj['compile_time'] = self.compile_time
        obj['compile_return'] = self.compile_return
        obj['run_time'] = self.run_time
        obj['run_return'] = self.run_return
        obj['finalize_time'] = self.finalize_time
        obj['checked_back'] = checked_back
        obj['results'] = results

        return obj

    def clean(self):
        self.kernel.clean()
        self.kernel = None
        self.kernel_args = None
