from hash_framework.config import config
import os, random
import json, time

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

    def create_cache_dir(self, dir_path):
        os.system("mkdir -p " + dir_path)
        if os.path.exists(dir_path + "/lock"):
            return False

        s = str(random.randint(100000000000000, 999999999999999))

        while True:
            f = open(dir_path + '/lock', 'w')
            f.write(s)
            f.close()

            time.sleep(0.01 * random.randint(1, 10))

            contents = open(dir_path + '/lock', 'r').read()
            if len(contents) == len(s):
                if contents == s:
                    return True
                return False

        return False

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

    def store_result(self, db, result):
        return []

    def load_result(self, db, rid):
        return []
