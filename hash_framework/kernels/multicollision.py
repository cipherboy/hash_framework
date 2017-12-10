from hash_framework.kernels.abstract import Kernel
import hash_framework.attacks as attacks
import hash_framework.algorithms as algorithms
from hash_framework.models import models
from hash_framework.config import config

import os.path, shutil
import json, subprocess
import itertools, time
import random

class Multicollision(Kernel):
    name = "ascii"

    def __init__(self, jid, args):
        super().__init__(jid, args)

        self.algo_type = algorithms.lookup(self.args['algo'])
        self.algo = self.algo_type()
        self.algo_name = self.args['algo']
        self.cms_args = self.args['cms_args']
        self.rounds = self.args['rounds']

        self.algo.rounds = self.rounds

        self.base = self.args['base']

        if 'h1_start_state' in self.args:
            self.h1_start_state = self.args['h1_start_state']
        else:
            self.h1_start_state = ""

        if 'h2_start_state' in self.args:
            self.h2_start_state = self.args['h2_start_state']
        else:
            self.h2_start_state = ""

    def gen_work(rounds, bases):
        work = []
        for i in range(0, len(bases)):
            base = list(bases[i])
            while len(base) < rounds:
                base.append('.'*32)
            bases[i] = tuple(base)

        for base in bases:
            work.append((rounds, base))

        print("Work: " + str(len(work)))
        return work

    def work_to_args(algo_name, work, start_state=None, start_block=None):
        rounds, base = work
        d =  {
            "algo": algo_name,
            "rounds": rounds,
            "cms_args": [],
            "base": base,
        }

        if start_state is not None:
            d["h1_start_state"] = start_state
            d["h2_start_state"] = start_state

        return d

    def on_result(algo, db, tags, work, wid, result):
        if type(result['results']) == list and len(result['results']) > 0:
            algo.rounds = work[wid][0]
            attacks.collision.import_db_multiple(algo, db, result['results'])

    def build_tag(self):
        return self.jid + self.build_cache_tag()

    def build_cache_tag(self):
        base = "mc-" + self.algo_name + "-r" + str(self.rounds)
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
                models.generate(self.algo, ['h1', 'h2', 'h3', 'h4'], rounds=self.rounds, bypass=True)
                attacks.collision.write_constraints(self.algo, prefixes=['h1', 'h2'], name="98-h1-h2-constraints.txt", out_name="ccollisionh1h2")
                attacks.collision.write_constraints(self.algo, prefixes=['h3', 'h4'], name="98-h3-h4-constraints.txt", out_name="ccollisionh3h4")
                attacks.collision.write_optional_differential(self.algo)
                attacks.collision.write_same_state(self.algo, prefixes=['h1', 'h2'], name="01-h1-h2-state.txt", out_name="cstateh1h2")
                attacks.collision.write_same_state(self.algo, prefixes=['h3', 'h4'], name="01-h3-h4-state.txt", out_name="cstateh3h4")
                attacks.collision.write_same_blocks(self.algo, prefixes=['h1', 'h3'], name="08-h1-h3-block.txt", out_name="cblocksh1h3")
                attacks.collision.write_same_blocks(self.algo, prefixes=['h2', 'h4'], name="08-h2-h4-block.txt", out_name="cblocksh2h4")

                models.vars.write_assign(['ccollisionh1h2', 'ccollisionh3h4', 'cblocks', 'cstateh1h2', 'cstateh3h4', 'cblocksh1h3', 'cblocksh2h4', 'cdifferentialsh1h2', 'cdifferentialsh3h4'])
                m.collapse(bc="00-combined-model.bc")

        while not os.path.exists(cache_path) or not os.path.exists(cache_path + "/00-combined-model.bc"):
            time.sleep(0.1)

        m = models()
        tag = self.build_tag()
        m.start(tag, False)
        base_path  = m.model_dir + "/" + tag
        os.system("ln -s " + cache_path + "/00-combined-model.bc " + base_path + "/00-combined-model.txt")

        attacks.collision.connected.loose.distributed_new_neighbor(self.algo, self.base, [], [], base_path + "/07-h1-h2-differential.txt", ['h1', 'h2'], 'cdifferentialsh1h2')
        attacks.collision.connected.loose.distributed_new_neighbor(self.algo, self.base, [], [], base_path + "/07-h3-h4-differential.txt", ['h3', 'h4'], 'cdifferentialsh3h4')

        if self.h1_start_state != '':
            models.vars.write_values(self.h1_start_state, 'h1s', base_path + "/01-h1-state.txt")

        if self.h2_start_state != '':
            models.vars.write_values(self.h2_start_state, 'h2s', base_path + "/01-h2-state.txt")

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
        run_model = m.cms_bin + " " + " ".join(m.cms_args) + " " + " ".join(self.cms_args)
        return model_files + " | " + compile_model + " | " + run_model

    def run_sat(self):
        m = models()
        tag = self.build_tag()
        out_file = self.out_path()
        cnf_file = self.cnf_path()

        model_files = "cat " + m.model_dir + "/" + tag + "/*.txt"
        compile_model = m.bc_bin + " " + " ".join(m.bc_args)
        cmd = model_files + " | " + compile_model

        of = open(cnf_file, 'w')
        oerr = open(cnf_file + ".err", 'w')

        ret = subprocess.call(cmd, shell=True, stdout=of, stderr=oerr)
        if ret != 0:
            return "An unknown error occurred while compiling the model (" + cmd + "): " + json.dumps(self.args)

        m.start(tag, False)
        rs = m.results(self.algo, out=out_file, cnf=cnf_file)

        return rs

    def run_unsat(self):
        if '--maxsol' in self.args['cms_args']:
            return self.run_sat()
        return []

    def clean(self):
        m = models()
        tag = self.build_tag()
        shutil.rmtree(m.model_dir + "/" + tag)
