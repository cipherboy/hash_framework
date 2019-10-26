from hash_framework.kernels.abstract import Kernel
import hash_framework.attacks as attacks
import hash_framework.algorithms as algorithms
from hash_framework.models import models
from hash_framework.config import Config

import os.path, shutil
import json, subprocess
import itertools, time
import random


class Minimal(Kernel):
    name = "minimal"

    def __init__(self, jid, args):
        super().__init__(jid, args)

        self.algo_type = algorithms.lookup(self.args["algo"])
        self.algo = self.algo_type()
        self.algo_name = self.args["algo"]
        self.cms_args = self.args["cms_args"]
        self.rounds = self.args["rounds"]
        self.algo.rounds = self.rounds

        self.bits = self.args["bits"]

        self.ascii = False
        self.both = False

        if "ascii" in self.args:
            self.ascii = self.args["ascii"]

        if "both" in self.args:
            self.both = self.args["both"]

        if "h1_start_state" in self.args:
            self.h1_start_state = self.args["h1_start_state"]
        else:
            self.h1_start_state = ""

        if "h2_start_state" in self.args:
            self.h2_start_state = self.args["h2_start_state"]
        else:
            self.h2_start_state = ""

        if "h1_start_block" in self.args:
            self.h1_start_block = self.args["h1_start_block"]
        else:
            self.h1_start_block = ""

        if "h2_start_block" in self.args:
            self.h2_start_block = self.args["h2_start_block"]
        else:
            self.h2_start_block = ""

    def gen_work(rounds, search_sizes):
        work = []

        for r in rounds:
            for s in search_sizes:
                for e in itertools.combinations(list(range(0, 32 * (r - 4))), s):
                    work.append((r, e))

        print("Work: " + str(len(work)))
        return work

    def gen_work_family(rounds, family, search_sizes):
        work = []

        var_set = []
        for pos in family:
            var_set += list(range(pos * 32, (pos + 1) * 32))

        for r in rounds:
            for s in search_sizes:
                for e in itertools.combinations(list(var_set), s):
                    if list(map(lambda x: x // 32, e)) == list(family):
                        work.append((r, e))

        print("Work: " + str(len(work)))
        return work

    def work_to_args(
        algo_name,
        work,
        start_state=None,
        start_block=None,
        ascii_block=False,
        both_ascii=False,
    ):
        rounds, bits = work
        d = {"algo": algo_name, "rounds": rounds, "cms_args": [], "bits": bits}

        if start_state is not None:
            d["h1_start_state"] = start_state
            d["h2_start_state"] = start_state

        if start_block is not None:
            d["h1_start_block"] = start_block

        if ascii_block:
            d["ascii"] = True

        if both_ascii:
            d["both"] = True

        return d

    def on_result(algo, db, result):
        if type(result["results"]) == list and len(result["results"]) > 0:
            attacks.collision.import_db_multiple(algo, db, result["results"])

    def store_result(self, db, result):
        algo = self.algo
        rids = attacks.collision.insert_db_multiple_automatic_tag(
            algo, db, result["results"], False
        )
        return rids

    def load_result(self, db, rids):
        algo = self.algo
        results = []
        for rid in rids:
            r = attacks.collision.load_db_single(algo, db, rid)
            results.append(r)
        return results

    def build_tag(self):
        return (
            str(self.jid)
            + self.build_cache_tag()
            + "-e"
            + "-".join(list(map(str, self.bits)))
        )

    def build_cache_tag(self):
        base = "min-" + self.algo_name + "-r" + str(self.rounds)
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
                attacks.collision.write_constraints(self.algo)
                attacks.collision.write_optional_differential(self.algo)
                attacks.collision.write_same_state(self.algo)

                models.vars.write_assign(
                    ["ccollision", "cblocks", "cstate", "cdifferentials", "cascii"]
                )
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

        differential_path = ["."] * (32 * self.rounds)
        for bit in self.bits:
            differential_path[bit] = "*"

        attacks.collision.differentials.write_path(
            self.algo,
            differential_path,
            clause="cdifferentials",
            name=base_path + "/09-differential.txt",
        )

        if self.ascii:
            prefixes = ["h1b"]
            if self.both:
                prefixes = ["h1b", "h2b"]

            attacks.collision.write_ascii_constraints(
                prefixes, base_path + "/44-ascii.txt"
            )

        if self.h1_start_state != "":
            models.vars.write_values(
                self.h1_start_state, "h1s", base_path + "/01-h1-state.txt"
            )

        if self.h1_start_block != "":
            models.vars.write_values(
                self.h1_start_block, "h1b", base_path + "/15-h1-state.txt"
            )

        if self.h2_start_state != "":
            models.vars.write_values(
                self.h2_start_state, "h2s", base_path + "/01-h2-state.txt"
            )

        if self.h2_start_block != "":
            models.vars.write_values(
                self.h2_start_block, "h2b", base_path + "/15-h2-state.txt"
            )

        cnf = self.cnf_path()
        o_cnf = open(cnf, "w")
        o_err = open(cnf + ".err", "w")
        model_files = "cat " + m.model_dir + "/" + tag + "/*.txt"
        compile_model = m.bc_bin + " " + " ".join(m.bc_args)
        cmd = model_files + " | " + compile_model
        ret = subprocess.call(
            cmd, stdin=subprocess.DEVNULL, stdout=o_cnf, stderr=o_err, shell=True
        )

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

        run_model = (
            m.cms_bin
            + " "
            + " ".join(m.cms_args)
            + " "
            + " ".join(self.cms_args)
            + " "
            + self.cnf_path()
        )
        return run_model

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
        shutil.rmtree(m.model_dir + "/" + tag)
