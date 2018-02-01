from hash_framework.boolean import *
from hash_framework.algorithms._sha3 import *
import functools, collections

class sha3:
    default_state_bits = ['F']*1600

    name = "sha3"
    rounds = 24
    block_size = 576
    state_size = 1600
    w = 64
    block_map = {}
    round_funcs = []
    output_vars = ["out" + str(i) for i in range(0, 1600)]

    generate_files = ["01-%s-sha3.txt"]

    def __init__(self, w=64, rounds=24):
        self.w = w
        self.state_size = 25*w
        self.rounds = rounds

    def evaluate(self, block, state, rounds=None):
        if rounds is None:
            rounds = self.rounds
        return compute_md5(block, state, rounds=rounds)

    def generate(self, prefixes=['h1', 'h2'], rounds=None):
        if rounds is None:
            rounds = self.rounds

        for prefix in prefixes:
            eval_table = {}
            state = [None] * self.state_size

            f = open("01-" + prefix + "-sha3.txt", 'w')
            perform_sha3(eval_table, state, f, prefix=prefix, rounds=rounds, w=self.w)

    def sanitize(self, eval_table):
        et = {}

        v = []
        for j in range(0, self.state_size):
            v.append(eval_table['in' + str(j)])
        et['i'] = ''.join(v)

        for i in range(0, self.rounds):
            # theta
            v = []
            for j in range(0, self.state_size):
                v.append(eval_table['r' + str(i) + 't' + str(j)])
            et['r' + str(i) + 't'] = ''.join(v)

            # rho
            v = []
            for j in range(0, self.state_size):
                v.append(eval_table['r' + str(i) + 'r' + str(j)])
            et['r' + str(i) + 'r'] = ''.join(v)

            # pi
            v = []
            for j in range(0, self.state_size):
                v.append(eval_table['r' + str(i) + 'p' + str(j)])
            et['r' + str(i) + 'p'] = ''.join(v)

            # chi
            v = []
            for j in range(0, self.state_size):
                v.append(eval_table['r' + str(i) + 'c' + str(j)])
            et['r' + str(i) + 'c'] = ''.join(v)

            # iota
            v = []
            for j in range(0, self.state_size):
                v.append(eval_table['r' + str(i) + 'i' + str(j)])
            et['r' + str(i) + 'i'] = ''.join(v)

        v = []
        for j in range(0, self.state_size):
            v.append(eval_table['out' + str(j)])
        et['out'] = ''.join(v)

        return et
