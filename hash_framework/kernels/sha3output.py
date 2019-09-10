from hash_framework.kernels.abstract import Kernel
import hash_framework.attacks as attacks
import hash_framework.algorithms as algorithms
from hash_framework.models import models
from hash_framework.config import config

import os.path, shutil
import json, subprocess
import itertools, time
import random


class SHA3Output(Kernel):
    name = "sha3output"

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

        self.margin = self.args["margin"]
        self.differences = self.args["differences"]

        self.sd = "-".join(map(str, self.differences))

    def gen_work(w, cdata, next_round, effective_margin):
        margin = (effective_margin // 64) * w
        if len(cdata) > 0:
            for d in cdata:
                if next_round == "r" or next_round == "p" or next_round[0] == "i":
                    args = {}
                    args["algo"] = "sha3"
                    args["cms_args"] = []
                    args["w"] = w
                    args["rounds"] = [next_round] + d[0]
                    args["margin"] = margin
                    args["differences"] = [d[1][0]] + d[1]
                    yield args
                else:
                    for nd in range(0, 25 * w):
                        if next_round == "t" and (nd % 2) != (d[1][0] % 2):
                            continue
                        args = {}
                        args["algo"] = "sha3"
                        args["cms_args"] = []
                        args["w"] = w
                        args["rounds"] = [next_round] + d[0]
                        args["margin"] = margin
                        args["differences"] = [nd] + d[1]
                        yield args

        else:
            for nd in range(0, 25 * w):
                args = {}
                args["algo"] = "sha3"
                args["cms_args"] = []
                args["w"] = w
                args["rounds"] = [next_round]
                args["margin"] = margin
                args["differences"] = [nd]
                yield args

    def build_tag(self):
        tag = (
            str(self.jid)
            + self.build_cache_tag()
            + "-m"
            + str(self.margin)
            + "-ie"
            + str(self.sd)
        )
        return tag

    def build_cache_tag(self):
        base = "s3m-" + self.algo_name + "-r" + self.srounds + "-w" + str(self.w)
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

                models.vars.write_assign(["ccollision", "cinput", "cintermediate"])
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
            cinput.append(("not", ("equal", "h1in" + str(i), "h2in" + str(i))))
        cinput = tuple(cinput)
        models.vars.write_range_clause(
            "cinput", self.differences[0], self.differences[0], cinput, "15-input.txt"
        )

        ccollision = ["and"]
        for i in range(0, self.margin):
            ccollision.append(("equal", "h1out" + str(i), "h2out" + str(i)))
        ccollision = tuple(ccollision)
        models.vars.write_clause("ccollision", ccollision, "20-collision.txt")

        if len(self.rounds) > 1:
            cintermediate = ["and", ("equal", "T", "T")]
            tir = 0
            rir = 0
            pir = 0
            cir = 0
            cic = 0
            for index in range(1, len(self.rounds)):
                r = self.rounds[index - 1]
                nerr = self.differences[index]
                if r[0] == "t":
                    cni = ["and"]
                    cvar = tir
                    for i in range(0, 25 * self.w):
                        cni.append(
                            (
                                "not",
                                (
                                    "equal",
                                    "h1r" + str(cvar) + r[0] + str(i),
                                    "h2r" + str(cvar) + r[0] + str(i),
                                ),
                            )
                        )
                    cni = tuple(cni)
                    models.vars.write_range_clause(
                        "cintermediate" + str(cic),
                        nerr,
                        nerr,
                        cni,
                        "39-intermediate-" + str(cic) + ".txt",
                    )
                    cintermediate.append("cintermediate" + str(cic))
                    cic += 1
                    tir += 1
                elif r[0] == "r":
                    cni = ["and"]
                    cvar = rir
                    for i in range(0, 25 * self.w):
                        cni.append(
                            (
                                "not",
                                (
                                    "equal",
                                    "h1r" + str(cvar) + r[0] + str(i),
                                    "h2r" + str(cvar) + r[0] + str(i),
                                ),
                            )
                        )
                    cni = tuple(cni)
                    models.vars.write_range_clause(
                        "cintermediate" + str(cic),
                        nerr,
                        nerr,
                        cni,
                        "39-intermediate-" + str(cic) + ".txt",
                    )
                    cintermediate.append("cintermediate" + str(cic))
                    cic += 1
                    rir += 1
                elif r[0] == "p":
                    cni = ["and"]
                    cvar = pir
                    for i in range(0, 25 * self.w):
                        cni.append(
                            (
                                "not",
                                (
                                    "equal",
                                    "h1r" + str(cvar) + r[0] + str(i),
                                    "h2r" + str(cvar) + r[0] + str(i),
                                ),
                            )
                        )
                    cni = tuple(cni)
                    models.vars.write_range_clause(
                        "cintermediate" + str(cic),
                        nerr,
                        nerr,
                        cni,
                        "39-intermediate-" + str(cic) + ".txt",
                    )
                    cintermediate.append("cintermediate" + str(cic))
                    cic += 1
                    pir += 1
                elif r[0] == "c":
                    cni = ["and"]
                    cvar = cir
                    for i in range(0, 25 * self.w):
                        cni.append(
                            (
                                "not",
                                (
                                    "equal",
                                    "h1r" + str(cvar) + r[0] + str(i),
                                    "h2r" + str(cvar) + r[0] + str(i),
                                ),
                            )
                        )
                    cni = tuple(cni)
                    models.vars.write_range_clause(
                        "cintermediate" + str(cic),
                        nerr,
                        nerr,
                        cni,
                        "39-intermediate-" + str(cic) + ".txt",
                    )
                    cintermediate.append("cintermediate" + str(cic))
                    cic += 1
                    cir += 1
                elif r[0] == "i":
                    iir = int(r[1:])
                    cni = ["and"]
                    cvar = iir
                    for i in range(0, 25 * self.w):
                        cni.append(
                            (
                                "not",
                                (
                                    "equal",
                                    "h1r" + str(cvar) + r[0] + str(i),
                                    "h2r" + str(cvar) + r[0] + str(i),
                                ),
                            )
                        )
                    cni = tuple(cni)
                    models.vars.write_range_clause(
                        "cintermediate" + str(cic),
                        nerr,
                        nerr,
                        cni,
                        "39-intermediate-" + str(cic) + ".txt",
                    )
                    cintermediate.append("cintermediate" + str(cic))
                    cic += 1
                else:
                    assert "Invalid round specification" == "Should not happen."

            cintermediate = tuple(cintermediate)
            models.vars.write_clause(
                "cintermediate", cintermediate, "40-intermediate.txt"
            )

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
        cnf_file = self.cnf_path()

        run_model = (
            m.cms_bin
            + " "
            + " ".join(m.cms_args)
            + " "
            + " ".join(self.cms_args)
            + " "
            + cnf_file
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
        os.chdir(m.model_dir)
        shutil.rmtree(m.model_dir + "/" + tag)
