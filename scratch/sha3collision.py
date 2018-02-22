#!/usr/bin/env python3

import hash_framework as hf
import sys, random

w = int(sys.argv[1])
factor = 64 // w
rounds = int(sys.argv[2])
count = 1
if len(sys.argv) == 4:
    count = int(sys.argv[3])

def __main__():
    m = hf.models()
    m.remote = False
    m.start("scratch-sha3-b" + str(w*25) + "-r" + str(rounds) + "-collision", True)
    m.cms_args = ['']
    hf.models.vars.write_header()

    output_margin = 512//factor
    input_margin = (25*w - 2*output_margin)

    algo = hf.algorithms.lookup('sha3')(w=w,rounds=rounds)
    algo.generate()

    ccollision = ['and']
    for i in range(0, output_margin):
        ccollision.append(('equal', 'h1out' + str(i), 'h2out' + str(i)))
    ccollision = tuple(ccollision)
    hf.models.vars.write_clause('ccollision', ccollision, '50-collision.txt')

    cinput = ['or']
    for i in range(0, input_margin):
        cinput.append(('not', ('equal', 'h1in' + str(i), 'h2in' + str(i))))
    cinput = tuple(cinput)
    hf.models.vars.write_clause('cinput', cinput, '52-input.txt')

    czero = ['and']
    for i in range(input_margin, 25*w):
        czero.append(('equal', 'h1in' + str(i), 'F'))
        czero.append(('equal', 'h2in' + str(i), 'F'))
    czero = tuple(czero)
    hf.models.vars.write_clause('czero', czero, '54-zero.txt')

    hf.models.vars.write_assign(['ccollision', 'cinput', 'czero'])
    m.collapse()
    m.build()
    r = m.run(count=count,random=random.randint(2, 1000000000))
    res = m.results(algo)
    print(len(res))
    for rs in res:
        obj = {}
        obj['w'] = w
        obj['rounds'] = rounds
        obj['input'] = hf.models.vars.compute_ddelta(rs['h1i'], rs['h2i'])[0:input_margin]
        for r in range(0, rounds):
            obj['r' + str(r)] = hf.models.vars.compute_ddelta(rs['h1r' + str(r) + 'i'], rs['h2r' + str(r) + 'i'])
        print(obj)

if __name__ == "__main__":
    __main__()
