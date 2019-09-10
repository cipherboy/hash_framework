from hash_framework.algorithms._sha3 import *
import functools, collections


class sha3:
    default_state_bits = ["F"] * 1600

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
        self.state_size = 25 * w
        self.rounds = rounds

    def evaluate(self, block, state, rounds=None):
        if rounds is None:
            rounds = self.rounds
        return compute_sha3(block, state, rounds=rounds)

    def generate(self, prefixes=["h1", "h2"], rounds=None):
        if rounds is None:
            rounds = self.rounds

        for prefix in prefixes:
            eval_table = {}
            state = [None] * self.state_size

            f = open("01-" + prefix + "-sha3.txt", "w")
            perform_sha3(eval_table, state, f, prefix=prefix, rounds=rounds, w=self.w)

    def sanitize(self, eval_table):
        et = {}

        v = []
        for j in range(0, self.state_size):
            v.append(eval_table["in" + str(j)])
        et["in"] = "".join(v)

        if type(self.rounds) == int:
            for i in range(0, self.rounds):
                # theta
                v = []
                for j in range(0, self.state_size):
                    v.append(eval_table["r" + str(i) + "t" + str(j)])
                et["r" + str(i) + "t"] = "".join(v)

                # rho
                v = []
                for j in range(0, self.state_size):
                    v.append(eval_table["r" + str(i) + "r" + str(j)])
                et["r" + str(i) + "r"] = "".join(v)

                # pi
                v = []
                for j in range(0, self.state_size):
                    v.append(eval_table["r" + str(i) + "p" + str(j)])
                et["r" + str(i) + "p"] = "".join(v)

                # chi
                v = []
                for j in range(0, self.state_size):
                    v.append(eval_table["r" + str(i) + "c" + str(j)])
                et["r" + str(i) + "c"] = "".join(v)

                # iota
                v = []
                for j in range(0, self.state_size):
                    v.append(eval_table["r" + str(i) + "i" + str(j)])
                et["r" + str(i) + "i"] = "".join(v)
        else:
            irs = {"t": 0, "r": 0, "p": 0, "c": 0}
            for r in self.rounds:
                if r[0] == "t" or r[0] == "r" or r[0] == "p" or r[0] == "c":
                    cir = irs[r[0]]
                    v = []
                    for j in range(0, self.state_size):
                        v.append(eval_table["r" + str(cir) + r[0] + str(j)])
                    et["r" + str(cir) + r[0]] = "".join(v)
                    irs[r[0]] += 1
                elif r[0] == "i":
                    ir = 0
                    if r[1] == "o" and r[2] == "t" and r[3] == "a":
                        ir = int(r[4:])
                    else:
                        ir = int(r[1:])
                    v = []
                    for j in range(0, self.state_size):
                        v.append(eval_table["r" + str(ir) + "i" + str(j)])
                    et["r" + str(ir) + "i"] = "".join(v)
                else:
                    assert "Invalid round specification" == "Should not happen."

        v = []
        for j in range(0, self.state_size):
            v.append(eval_table["out" + str(j)])
        et["out"] = "".join(v)

        return et
