from hash_framework.config import config
import os.path

class Kernel:
    def __init__(self, args, timeout):
        self.args = args
        self.timeout = None
        pass

    def cache_dir(self):
        return config.cache_dir

    def pre_run(self):
        pass

    def out_path(self):
        return "problem.out"

    def run_cmd(self):
        return "echo 'Please override Kernel and supply a run_cmd method.'"

    def post_run(self, obj, data):
        if obj["return"] == 10:
            return self.run_sat(obj["out"], data, raw=obj)
        elif obj["return"] == 20:
            return self.run_unsat(obj["out"], data, raw=obj)
        else:
            return self.run_error(obj["out"], data, raw=obj)

    def run_sat(self, path, data, raw=None):
        pass

    def run_unsat(self, path, data, raw=None):
        pass

    def run_error(self, path, data, raw=None):
        print("[Error]")
        print(raw)
