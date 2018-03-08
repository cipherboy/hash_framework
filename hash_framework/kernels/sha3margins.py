from hash_framework.kernels.abstract import Kernel
import hash_framework.attacks as attacks
import hash_framework.algorithms as algorithms
from hash_framework.models import models
from hash_framework.config import config

import os.path, shutil
import json, subprocess
import itertools, time
import random

class SHA3Margins(Kernel):
    name = "sha3margins"

    def __init__(self, jid, args):
        super().__init__(jid, args)

        assert(self.args['algo'] == 'sha3')

        self.algo_type = algorithms.lookup(self.args['algo'])
        self.algo = self.algo_type()
        self.algo_name = self.args['algo']
        self.cms_args = self.args['cms_args']
        self.rounds = self.args['rounds']

        self.w = self.args['w']
        self.algo.rounds = self.rounds

        self.input_fill = self.args['input_fill']
        self.input_margin = self.args['input_margin']
        self.intermediate_margins = self.args['intermediate_margins']
        self.output_margin = self.args['output_margin']

    def gen_work(rounds, bases):
        work = []

        print("TODO")

        return work

    def work_to_args(algo_name, work, start_state=None, start_block=None):
        print("TODO")
        rounds, base, ones = work
        d =  {
            "algo": algo_name,
            "rounds": rounds,
            "cms_args": [],
            "base": base,
            "ones": ones,
        }

        if start_state is not None:
            d["h1_start_state"] = start_state
            d["h2_start_state"] = start_state

        return d

    def on_result(algo, db, result):
        print("TODO")
        if type(result['results']) == list and len(result['results']) > 0:
            attacks.collision.import_db_multiple(algo, db, result['results'])

    def store_result(self, db, result):
        algo = self.algo
        rids = attacks.collision.insert_db_multiple_automatic_tag(algo, db, result['results'], False)
        return rids

    def load_result(self, db, rids):
        algo = self.algo
        results = []
        for rid in rids:
            r = attacks.collision.load_db_single(algo, db, rid)
            results.append(r)
        return results

    def build_tag(self):
        return self.jid + self.build_cache_tag() + "-o" + str(self.ones)

    def build_cache_tag(self):
        base = "o-" + self.algo_name + "-r" + str(self.rounds)
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
                models.generate(self.algo, ['h1', 'h2'], rounds=self.rounds, bypass=True)
                attacks.collision.write_constraints(self.algo)
                attacks.collision.write_optional_differential(self.algo)
                attacks.collision.write_same_state(self.algo)

                models.vars.write_assign(['ccollision', 'cblocks', 'cstate', 'cdifferentials', 'cones'])
                m.collapse(bc="00-combined-model.bc")

        while not os.path.exists(cache_path) or not os.path.exists(cache_path + "/00-combined-model.bc"):
            time.sleep(0.1)

        m = models()
        tag = self.build_tag()
        m.start(tag, False)
        base_path  = m.model_dir + "/" + tag
        os.system("ln -s " + cache_path + "/00-combined-model.bc " + base_path + "/00-combined-model.txt")

        attacks.collision.connected.loose.distributed_new_neighbor(self.algo, self.base, [], [], base_path + "/07-differential.txt")

        f = open(base_path + "/43-ones.txt", 'w')
        f.write("cones := [" + str(self.ones) + "," + str(self.ones) + "](" + ','.join(map(lambda x: 'h1b' + str(x), range(512))) + ");")
        f.flush()
        f.close()


        if self.h1_start_state != '':
            models.vars.write_values(self.h1_start_state, 'h1s', base_path + "/01-h1-state.txt")

        if self.h2_start_state != '':
            models.vars.write_values(self.h2_start_state, 'h2s', base_path + "/01-h2-state.txt")

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
        rg = m.results_generator(self.algo, out=out_file, cnf=cnf_file)

        result = []
        for r in rg:
            result.append({'data': "", 'row': r})

        return result

    def run_unsat(self):
        if '--maxsol' in self.args['cms_args']:
            return self.run_sat()
        return []

    def clean(self):
        m = models()
        tag = self.build_tag()
        shutil.rmtree(m.model_dir + "/" + tag)
