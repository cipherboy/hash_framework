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

        self.w = self.args['w']
        self.rounds = self.args['rounds']
        self.algo_type = algorithms.lookup(self.args['algo'])
        self.algo = self.algo_type(w=self.w, rounds=self.rounds)
        self.algo_name = self.args['algo']
        self.cms_args = self.args['cms_args']

        if type(self.rounds) == int:
            self.srounds = str(self.rounds)
        elif type(self.rounds) == list:
            self.srounds = '-'.join(map(str, self.rounds))

        self.input_fill = self.args['input_fill']
        self.input_margin = self.args['input_margin']
        self.input_error = self.args['input_error']
        self.intermediate_margins = self.args['intermediate_margins']
        self.output_margin = self.args['output_margin']
        self.output_error = self.args['output_error']

    def gen_work(rounds, w, input_errors, output_errors, input_fill=""):
        # Function Margins
        if input_fill == "":
            input_fill = 'F' * (25*w)

        for input_error in input_errors:
            for output_error in output_errors:
                for input_margin in range(input_error, 25*w):
                    for output_margin in range(output_error, 25*w):
                        args = {}
                        args['algo'] = 'sha3'
                        args['cms_args'] = []
                        args['w'] = w
                        args['rounds'] = rounds
                        args['input_fill'] = input_fill[input_margin:25*w]
                        args['input_margin'] = input_margin
                        args['input_error'] = input_error
                        args['intermediate_margins'] = []
                        args['output_margin'] = output_margin
                        args['output_error'] = output_error
                        yield args

    def build_tag(self):
        tag = str(self.jid) + self.build_cache_tag() + "-i" + str(self.input_margin)
        tag += "-o" + str(self.output_margin) + "-int" + '-'.join(map(str, self.intermediate_margins))
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
                models.generate(self.algo, ['h1', 'h2'], rounds=self.rounds, bypass=True)

                models.vars.write_assign(['cstart', 'cinput', 'cintermediate', 'coutput'])
                m.collapse(bc="00-combined-model.bc")

        while not os.path.exists(cache_path) or not os.path.exists(cache_path + "/00-combined-model.bc"):
            time.sleep(0.1)

        m = models()
        tag = self.build_tag()
        m.start(tag, False)
        base_path  = m.model_dir + "/" + tag
        os.system("ln -s " + cache_path + "/00-combined-model.bc " + base_path + "/00-combined-model.txt")

        cstart = models.vars.differential(self.input_fill, 'h1in', self.input_margin, 'h2in', self.input_margin)
        models.vars.write_clause('cstart', cstart, '50-start.txt')

        tail = '*'*self.input_margin
        cinput = models.vars.differential(tail, 'h1in', 0, 'h2in', 0)
        models.vars.write_range_clause('cinput', self.input_error, self.input_error, cinput, '50-input.txt')

        tail = '*'*self.output_margin
        coutput = models.vars.differential(tail, 'h1out', 0, 'h2out', 0)
        models.vars.write_range_clause('coutput', self.output_error, self.output_error, coutput, '50-output.txt')

        cnf_file = self.cnf_path()

        model_files = "cat " + m.model_dir + "/" + tag + "/*.txt"
        compile_model = m.bc_bin + " " + " ".join(m.bc_args)
        cmd = model_files + " | " + compile_model

        of = open(cnf_file, 'w')
        oerr = open(cnf_file + ".err", 'w')

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
        run_model = m.cms_bin + " " + " ".join(m.cms_args) + " " + " ".join(self.cms_args)
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
            print(r)
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
