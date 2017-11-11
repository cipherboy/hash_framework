from hash_framework.kernels.abstract import Kernel
import hash_framework.attacks as attacks
import hash_framework.algorithms as algorithms
from hash_framework.models import models
from hash_framework.config import config

import os.path

class SecondPreimage(Kernel):
    def __init__(self, args):
        super().__init__(args)
        self.algo = algorithms.lookup(self.args['algo'])
        self.algo_name = self.args['algo']
        self.cms_args = self.args['cms_args']
        self.rounds = self.args['rounds']
        self.algo.rounds = self.rounds
        self.places = self.args['places']
        self.h1_start_state = self.args['h1_start_state']
        self.h2_start_state = self.args['h2_start_state']
        self.h1_start_block = self.args['h1_start_block']
        self.h2_start_block = self.args['h2_start_block']

    def build_tag(self):
        return self.build_cache_tag() + "-e" + '-'.join(list(map(str, self.places)))

    def build_cache_tag(self):
        return "sp-" + self.algo_name + "-r" + self.rounds

    def build_cache_path(self):
        return self.cache_dir() + "/" + self.build_cache_tag()

    def pre_run(self):
        cache_path = self.build_cache_path()
        cache_tag = self.build_cache_tag()

        if not os.path.exists(cache_path)
            m = models()
            m.model_dir = self.cache_dir()
            m.start(cache_tag, False)
            models.vars.write_header()
            models.generate(self.algo, ['h1', 'h2'], rounds=self.rounds, bypass=True)
            attacks.collision.write_constraints(self.algo)
            attacks.collision.write_optional_differential(self.algo)
            models.vars.write_assign(['ccollision', 'cblocks', 'cstate', 'cdifferentials', 'cnegated'])
            m.collapse(bc="00-combined-model.txt")

        m = models()
        tag = self.build_tag()
        m.start(tag, False)
        os.system("ln -s " + cache_path + "/00-combined-model.txt " + m.model_dir + "/" + tag + "/00-combined-model.txt")

        if self.h1_start_state != '':
            models.vars.write_values(self.h1_start_state, 'h1s', "01-h1-state.txt")
        if self.h1_start_block != '':
            models.vars.write_values(self.h1_start_block, 'h1b', "15-h1-state.txt")
        if self.h2_start_state != '':
            models.vars.write_values(self.h2_start_state, 'h2s', "01-h2-state.txt")
        if self.h2_start_block != '':
            models.vars.write_values(self.h2_start_block, 'h2b', "15-h2-state.txt")

        attacks.collision.reduced.specified_difference(algo, e)
        m.collapse()

    def out_path(self):
        m = models()
        tag = self.build_tag()
        return m.model_dir + "/" + tag + "/problem.out"

    def run_cmd(self):
        m = models()

        model_files = "cat " +  + "*.txt"
        compile_model = m.bc_bin + " " + " ".join(m.bc_args)
        run_model = m.cms_bin + " " + " ".join(m.cms_args) + " " + " ".join(self.cms_args)
        return models_files + " | " + compile_model + " " + run_model
