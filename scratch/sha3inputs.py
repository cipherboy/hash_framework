#!/usr/bin/env python3

import json, sys
import hash_framework as hf

def __main__():
    for w in [2]:
        for rounds in range(1, 2):
            factor = 64 // w
            output_margin = 512//factor
            input_margin = (25*w - 2*output_margin)

            algo = hf.algorithms.lookup('sha3')(w=w,rounds=rounds)

            m = hf.models()
            m.remote = False
            m.start("scratch-sha3-b" + str(25*w) + "-r" + str(rounds) + "-collision", False)
            n_inputs = set()

            count = 0
            double_expansions = 0
            subset_expansions = 0
            not_expansion = 0

            f = open('/home/cipherboy/GitHub/hash_framework/scratch/collisions-w' + str(w) + '-r' + str(rounds) + ".txt", 'w')
            print(f)
            f.flush()
            for rs in m.results_generator(algo):
                obj = {}
                obj['w'] = w
                obj['rounds'] = rounds
                obj['h1input'] = rs['h1i']
                obj['h2input'] = rs['h2i']
                obj['dinput'] = hf.models.vars.compute_ddelta(rs['h1i'], rs['h2i'])
                obj['rinput'] = hf.models.vars.compute_ddelta(rs['h1i'], rs['h2i'])
                for r in range(0, rounds):
                    obj['h1r' + str(r)] = rs['h1r' + str(r) + 'i']
                    obj['h2r' + str(r)] = rs['h2r' + str(r) + 'i']
                    obj['dr' + str(r)] = hf.models.vars.compute_ddelta(rs['h1r' + str(r) + 'i'], rs['h2r' + str(r) + 'i'])
                    obj['rr' + str(r)] = hf.models.vars.compute_ddelta(rs['h1r' + str(r) + 'i'], rs['h2r' + str(r) + 'i'])
                f.write(str(obj) + "\n")
            f.flush()
            f.close()


if __name__ == "__main__":
    __main__()
