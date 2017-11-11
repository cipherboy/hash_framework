from hash_framework.config import config
import os.path
import json

class Kernel:
    def __init__(self, jid, args):
        self.jid = jid
        self.args = args

    def cache_dir(self):
        return config.cache_dir

    def gen_work():
        pass

    def work_to_args():
        pass

    def pre_run(self):
        pass

    def out_path(self):
        return "problem.out"

    def run_cmd(self):
        return "echo 'Please override Kernel and supply a run_cmd method.'"

    def post_run(self, return_code):
        if return_code == 10:
            return self.run_sat()
        elif return_code == 20:
            return self.run_unsat()
        else:
            return self.run_error()

    def run_sat(self):
        return []

    def run_unsat(self):
        return []

    def run_error(self):
        print("[Error running model]: " + json.dumps(self.args))

    def clean(self):
        pass
