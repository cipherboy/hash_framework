from hash_framework.kernels.abstract import Kernel
import hash_framework.attacks as attacks
import hash_framework.algorithms as algorithms
from hash_framework.models import models
from hash_framework.config import Config

import os.path, shutil
import json, subprocess
import itertools, time
import random


class SHA3Distributivity(Kernel):
    name = "sha3distributivity"

    def __init__(self, jid, args):
        super().__init__(jid, args)

        assert self.args["algo"] == "sha3"

        self.w = self.args["w"]
        self.rounds = self.args["rounds"]
        self.algo_type = algorithms.lookup(self.args["algo"])
        self.algo = self.algo_type(w=self.w, rounds=self.rounds)
        self.algo_name = self.args["algo"]
        self.cms_args = self.args["cms_args"]

        if type(self.rounds) == int:
            self.srounds = str(self.rounds)
        elif type(self.rounds) == list:
            self.srounds = "-".join(map(str, self.rounds))

    def gen_work(rounds, ws):
        for r in rounds:
            for w in ws:
                args = {}
                args["algo"] = "sha3"
                args["cms_args"] = []
                args["w"] = w
                args["rounds"] = r
                yield args

    def build_tag(self):
        tag = str(self.jid) + self.build_cache_tag()
        return tag

    def build_cache_tag(self):
        base = "s3dist-" + self.algo_name + "-r" + self.srounds + "-w" + str(self.w)
        return base

    def build_cache_path(self):
        return self.cache_dir() + "/" + self.build_cache_tag()

    def pre_run(self):
        cache_path = self.build_cache_path()
        cache_tag = self.build_cache_tag()

        if not os.path.exists(cache_path):
            count = 0
            m = models()
            m.model_dir = self.cache_dir()
            cache_dir_path = m.model_dir + "/" + cache_tag

            if self.create_cache_dir(cache_dir_path):
                m.start(cache_tag, False)
                models.vars.write_header()
                models.generate(
                    self.algo, ["h1", "h2", "h3"], rounds=self.rounds, bypass=True
                )

                models.vars.write_assign(["cinput", "coutput"])
                m.collapse(bc="00-combined-model.bc")

        while not os.path.exists(cache_path) or not os.path.exists(
            cache_path + "/00-combined-model.bc"
        ):
            time.sleep(0.1)

        m = models()
        tag = self.build_tag()
        m.start(tag, False)
        base_path = m.model_dir + "/" + tag
        os.system(
            "ln -s "
            + cache_path
            + "/00-combined-model.bc "
            + base_path
            + "/00-combined-model.txt"
        )

        cinput = ["and"]
        for i in range(0, 25 * self.w):
            cinput.append(
                ("equal", "h1in" + str(i), ("xor", "h2in" + str(i), "h3in" + str(i)))
            )
        cinput = tuple(cinput)
        models.vars.write_clause("cinput", cinput, "50-input.txt")

        coutput = ["and"]
        for i in range(0, 25 * self.w):
            coutput.append(
                ("equal", "h1out" + str(i), ("xor", "h2out" + str(i), "h3out" + str(i)))
            )
        coutput = ("not", tuple(coutput))
        models.vars.write_clause("coutput", coutput, "50-output.txt")

        cnf_file = self.cnf_path()

        model_files = "cat " + m.model_dir + "/" + tag + "/*.txt"
        compile_model = m.bc_bin + " " + " ".join(m.bc_args)
        cmd = model_files + " | " + compile_model

        of = open(cnf_file, "w")
        oerr = open(cnf_file + ".err", "w")

        ret = subprocess.call(cmd, shell=True, stdout=of, stderr=oerr)
        return ret

    def out_path(self):
        m = models()
        tag = self.build_tag()
        return m.model_dir + "/" + tag + "/problem.out"

    def cnf_path(self):
        m = models()
        tag = self.build_tag()
        return m.model_dir + "/" + tag + "/problem.cnf"

    def run_cmd(self):
        m = models()
        tag = self.build_tag()

        model_files = "cat " + m.model_dir + "/" + tag + "/*.txt"
        compile_model = m.bc_bin + " " + " ".join(m.bc_args)
        run_model = (
            m.cms_bin + " " + " ".join(m.cms_args) + " " + " ".join(self.cms_args)
        )
        return model_files + " | " + compile_model + " | " + run_model

    def run_sat(self):
        m = models()
        tag = self.build_tag()
        out_file = self.out_path()
        cnf_file = self.cnf_path()

        m.start(tag, False)
        rg = m.results_generator(
            self.algo, out=out_file, cnf=cnf_file, prefixes=["h1", "h2", "h3"]
        )

        result = []
        for r in rg:
            result.append({"data": "", "row": r})

        return result

    def run_unsat(self):
        if "--maxsol" in self.args["cms_args"]:
            return self.run_sat()
        return []

    def clean(self):
        m = models()
        tag = self.build_tag()
        os.chdir(m.model_dir)
        shutil.rmtree(m.model_dir + "/" + tag)
