from hash_framework.kernels.abstract import Kernel
import hash_framework.attacks as attacks
import hash_framework.algorithms as algorithms
from hash_framework.models import models
from hash_framework.config import Config

import os.path, shutil
import json, subprocess
import itertools, time
import random


class SHA3Bijectivity(Kernel):
    name = "sha3bijections"

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

    def gen_work():
        # Function Margins
        round_funcs = ["t", "r", "p", "c", "i"]
        for w in [1, 2, 4, 8, 16, 32, 64]:
            args = {}
            args["algo"] = "sha3"
            args["cms_args"] = []
            args["w"] = w
            args["rounds"] = ["r"]
            yield args
            args["rounds"] = ["p"]
            yield args
            args["rounds"] = ["c"]
            yield args
            args["rounds"] = ["i0"]
            yield args

            for l in range(0, 24):
                base = []
                ir = 0
                for i in range(0, l):
                    base.append("t")
                    base.append("r")
                    base.append("p")
                    base.append("c")
                    base.append("i" + str(ir))
                    ir += 1

                base.append("t")
                args = {}
                args["algo"] = "sha3"
                args["cms_args"] = []
                args["w"] = w
                args["rounds"] = base
                yield args
                base.append("r")
                args["rounds"] = base
                yield args
                base.append("p")
                args["rounds"] = base
                yield args
                base.append("c")
                args["rounds"] = base
                yield args
                base.append("i" + str(ir))
                args["rounds"] = base
                yield args

    def build_tag(self):
        tag = str(self.jid) + self.build_cache_tag()
        return tag

    def build_cache_tag(self):
        base = "s3b-" + self.algo_name + "-r" + self.srounds + "-w" + str(self.w)
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
                    self.algo, ["h1", "h2"], rounds=self.rounds, bypass=True
                )

                models.vars.write_assign(["cbijection"])
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

        cinin = ["and"]
        for i in range(0, 25 * self.w):
            cinin.append(("equal", "h1in" + str(i), "h2in" + str(i)))
        cinin = ("not", tuple(cinin))
        models.vars.write_clause("cinin", cinin, "02-inin.txt")
        cinout = ["and"]
        for i in range(0, 25 * self.w):
            cinout.append(("equal", "h1out" + str(i), "h2out" + str(i)))
        cinout = tuple(cinout)
        models.vars.write_clause("cinout", cinout, "02-inout.txt")

        csurin = ["and"]
        for i in range(0, 25 * self.w):
            csurin.append(("equal", "h1in" + str(i), "h2in" + str(i)))
        csurin = tuple(csurin)
        models.vars.write_clause("csurin", csurin, "02-surin.txt")
        csurout = ["and"]
        for i in range(0, 25 * self.w):
            csurout.append(("equal", "h1out" + str(i), "h2out" + str(i)))
        csurout = ("not", tuple(csurout))
        models.vars.write_clause("csurout", csurout, "02-surout.txt")

        cinjection = ("and", "cinin", "cinout")
        csurjection = ("and", "csurin", "csurout")
        cbijection = ("or", cinjection, csurjection)
        models.vars.write_clause("cbijection", cbijection, "98-problem.txt")

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
        rg = m.results_generator(self.algo, out=out_file, cnf=cnf_file)

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
