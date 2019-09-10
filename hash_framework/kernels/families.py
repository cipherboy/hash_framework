from hash_framework.kernels.abstract import Kernel
import hash_framework.attacks as attacks
import hash_framework.algorithms as algorithms
from hash_framework.models import models
from hash_framework.config import config

import os.path, shutil
import json, subprocess
import itertools, time
import random


class Families(Kernel):
    name = "families"

    def __init__(self, jid, args):
        super().__init__(jid, args)

        self.algo_type = algorithms.lookup(self.args["algo"])
        self.algo = self.algo_type()
        self.algo_name = self.args["algo"]
        self.cms_args = self.args["cms_args"]
        self.rounds = self.args["rounds"]
        self.algo.rounds = self.rounds
        self.places = self.args["places"]

        if "invalid" in self.args:
            self.invalid = self.args["invalid"]
        else:
            self.invalid = False

        if "specific" in self.args:
            self.specific = self.args["specific"]
        else:
            self.specific = None

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

        self.ascii = []
        if "ascii" in self.args:
            self.ascii = self.args["ascii"]

    def gen_work(round_set, size_set):
        work = set()
        for r in round_set:
            for s in size_set:
                for e in itertools.combinations(list(range(0, r - 4)), s):
                    work.add((r, e))
        print("Work: " + str(len(work)))
        return list(work)

    def gen_work_extension(existing, rounds):
        ext_rounds = list(range(rounds - 4, rounds))
        for w in existing:
            for r in range(0, 5):
                for n in itertools.combinations(ext_rounds, r):
                    ns = set(w[1]).union(set(n))
                    yield (rounds, tuple(sorted(list(ns))))

    def work_to_args(
        algo_name,
        work,
        cascii=False,
        h1_start_state="",
        h1_start_block="",
        h2_start_state="",
        h2_start_block="",
    ):
        d = {"algo": algo_name, "rounds": work[0], "cms_args": [], "places": work[1]}

        if cascii:
            d["ascii"] = ["h1b", "h2b"]

        if h1_start_state != "":
            d["h1_start_state"] = h1_start_state

        if h1_start_block != "":
            d["h1_start_block"] = h1_start_block

        if h2_start_state != "":
            d["h2_start_state"] = h2_start_state

        if h2_start_block != "":
            d["h2_start_block"] = h2_start_block

        return d

    def work_to_tag(algo_name, work):
        return algo_name + "-r" + str(work[0]) + "-e" + "-".join(map(str, work[1]))

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
            + "-".join(list(map(str, self.places)))
        )

    def build_cache_tag(self):
        base = "sp-" + self.algo_name + "-r" + str(self.rounds)
        if self.invalid:
            base += "-iT"
        if self.specific:
            base += "-s" + str(len(self.specific))
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
                if self.invalid:
                    invalid_differentials = models.vars.differentials(
                        [
                            ["." * 32, "h1b", 96, "h2b", 96],
                            ["." * 32, "h1b", 224, "h2b", 224],
                            ["." * 32, "h1b", 352, "h2b", 352],
                            ["." * 32, "h1b", 480, "h2b", 480],
                        ]
                    )
                    models.vars.write_clause(
                        "cinvalid", invalid_differentials, "23-invalid.txt"
                    )

                models.vars.write_assign(
                    [
                        "ccollision",
                        "cblocks",
                        "cstate",
                        "cdifferentials",
                        "cinvalid",
                        "cnegated",
                        "cspecific",
                        "cascii",
                    ]
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

        if self.specific != None:
            specific_differentials = models.vars.differentials(self.specific)
            models.vars.write_clause(
                "cspecific", specific_differentials, "28-specific.txt"
            )

        attacks.collision.reduced.specified_difference(
            self.algo, self.places, base_path + "/07-differential.txt"
        )

        attacks.collision.write_ascii_constraints(self.ascii, 64)

        cnf = self.cnf_path()
        o_cnf = open(cnf, "w")
        o_err = open(cnf + ".err", "w")
        model_files = "cat " + m.model_dir + "/" + tag + "/*.txt"
        compile_model = m.bc_bin + " " + " ".join(m.bc_args)
        cmd = model_files + " | " + compile_model
        ret = subprocess.call(
            cmd, stdin=subprocess.DEVNULL, stdout=o_cnf, stderr=o_err, shell=True
        )

        if not o_cnf.closed:
            o_cnf.flush()
            o_cnf.close()

        if not o_err.closed:
            o_err.flush()
            o_err.close()

        if ret != 0:
            print("ERROR COMPILING MODEL: " + tag)
            return ret

        return 0

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

        print(result)

        return result

    def run_unsat(self):
        if "--maxsol" in self.args["cms_args"]:
            return self.run_sat()
        return []

    def clean(self):
        m = models()
        tag = self.build_tag()
        shutil.rmtree(m.model_dir + "/" + tag)
