from hash_framework.kernels.abstract import Kernel
from hash_framework.config import config

import os.path, shutil
import json, subprocess
import itertools, time
import random

class Test(Kernel):
    def __init__(self, jid, args):
        self.jid = jid
        self.args = args
        self.data = {}
        self.results = []

    def cache_dir(self):
        return config.cache_dir

    def gen_work():
        pass

    def work_to_args():
        pass

    def pre_run(self):
        if 'test_install' in self.args:
            self.data['config.bc_path'] = config.bc_bin
            self.data['config.bc_path.valid'] = os.path.exists(config.bc_bin)
            self.data['config.cms_path'] = config.cms_bin
            self.data['config.cms_path.valid'] = os.path.exists(config.cms_bin)
            self.data['config.master_uri'] = config.master_uri
            self.data['config.job_count'] = config.job_count

        compile_sleep = random.uniform(self.args['compile.min'], self.args['compile.max'])
        time.sleep(compile_sleep)

    def create_cache_dir(self, dir_path):
        pass

    def out_path(self):
        return ""

    def run_cmd(self):
        self.data['test.sleep_time'] = random.uniform(self.args['cmd.min'], self.args['cmd.max'])
        return "sleep " + str(self.data['test.sleep_time'])

    def post_run(self, return_code):
        results_sleep = random.uniform(self.args['results.min'], self.args['results.max'])
        time.sleep(results_sleep)

        row_test = {'name': self.args['row_name'], 'value': self.args['row_value']}
        return [{'data': self.data, 'row': row_test}]

    def clean(self):
        pass
