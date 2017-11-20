from hash_framework.kernels.abstract import Kernel
import hash_framework.attacks as attacks
import hash_framework.algorithms as algorithms
from hash_framework.models import models
from hash_framework.config import config

import os.path, shutil
import json, subprocess
import itertools, time
import random

class SecondPreimage(Kernel):
    def __init__(self, jid, args):
        super().__init__(jid, args)

        self.algo_type = algorithms.lookup(self.args['algo'])
        self.algo = self.algo_type()
        self.algo_name = self.args['algo']
        self.cms_args = self.args['cms_args']
        self.rounds = self.args['rounds']
        self.algo.rounds = self.rounds
        self.places = self.args['places']

        if 'invalid' in self.args:
            self.invalid = self.args['invalid']
        else:
            self.invalid = False

        if 'specific' in self.args:
            self.specific = self.args['specific']
        else:
            self.specific = None

        if 'h1_start_state' in self.args:
            self.h1_start_state = self.args['h1_start_state']
        else:
            self.h1_start_state = ""

        if 'h2_start_state' in self.args:
            self.h2_start_state = self.args['h2_start_state']
        else:
            self.h2_start_state = ""

        if 'h1_start_block' in self.args:
            self.h1_start_block = self.args['h1_start_block']
        else:
            self.h1_start_block = ""

        if 'h2_start_block' in self.args:
            self.h2_start_block = self.args['h2_start_block']
        else:
            self.h2_start_block = ""

    def gen_work(round_set, size_set):
        work = set()
        for r in round_set:
            for s in size_set:
                for e in itertools.combinations(list(range(0, r-4)), s):
                    work.add((r, e))
        print("Work: " + str(len(work)))
        return list(work)

    def work_to_args(algo_name, start_state, start_block, work):
        d =  {
            "algo": algo_name,
            "rounds": work[0],
            "cms_args": [],
            "places": work[1],
            "h1_start_state": start_state,
            "h2_start_state": start_state,
            "h1_start_block": start_block,
            #"invalid": True,
            #"specific": [['.'*32, 'h1b', i*32, 'h2b', i*32] for i in [0, 12]]
        }

        return d

    def work_to_tag(algo_name, work):
        return algo_name + "-r" + str(work[0]) + "-e" + '-'.join(map(str, work[1]))

    def on_result(algo, db, tags, work, wid, result):
        tag = tags[wid]
        if type(result['results']) == list and len(result['results']) > 0:
            algo.rounds = work[wid][0]
            attacks.collision.insert_db_multiple(algo, db, result['results'], tag, False)

    def build_tag(self):
        return self.jid + self.build_cache_tag() + "-e" + '-'.join(list(map(str, self.places)))

    def build_cache_tag(self):
        base = "sp-" + self.algo_name + "-r" + str(self.rounds)
        if self.invalid:
            base += '-iT'
        if self.specific:
            base += '-s' + str(len(self.specific))
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
                if self.invalid:
                    invalid_differentials = models.vars.differentials([['.'*32, 'h1b', 96, 'h2b', 96], ['.'*32, 'h1b', 224, 'h2b', 224], ['.'*32, 'h1b', 352, 'h2b', 352], ['.'*32, 'h1b', 480, 'h2b', 480]])
                    models.vars.write_clause('cinvalid', invalid_differentials, '23-invalid.txt')

                models.vars.write_assign(['ccollision', 'cblocks', 'cstate', 'cdifferentials', 'cinvalid', 'cnegated', 'cspecific'])
                m.collapse(bc="00-combined-model.bc")
        while not os.path.exists(cache_path) or not os.path.exists(cache_path + "/00-combined-model.bc"):
            time.sleep(0.1)

        m = models()
        tag = self.build_tag()
        m.start(tag, False)
        base_path  = m.model_dir + "/" + tag
        os.system("ln -s " + cache_path + "/00-combined-model.bc " + base_path + "/00-combined-model.txt")

        if self.h1_start_state != '':
            models.vars.write_values(self.h1_start_state, 'h1s', base_path + "/01-h1-state.txt")
        if self.h1_start_block != '':
            models.vars.write_values(self.h1_start_block, 'h1b', base_path + "/15-h1-state.txt")
        if self.h2_start_state != '':
            models.vars.write_values(self.h2_start_state, 'h2s', base_path + "/01-h2-state.txt")
        if self.h2_start_block != '':
            models.vars.write_values(self.h2_start_block, 'h2b', base_path + "/15-h2-state.txt")

        if self.specific != None:
            specific_differentials = models.vars.differentials(self.specific)
            models.vars.write_clause('cspecific', specific_differentials, '28-specific.txt')

        attacks.collision.reduced.specified_difference(self.algo, self.places, base_path + "/07-differential.txt")

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
