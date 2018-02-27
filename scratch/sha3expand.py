#!/usr/bin/env python3

import hash_framework as hf
import sys

def __main__():
    in_objs = []
    in_obj = in_objs[0]

    ow = in_obj['w']
    w = ow * 2
    factor = 64 // w
    rounds = in_obj['rounds']

    m = hf.models()
    m.remote = False
    m.start("scratch-sha3-b" + str(w*25) + "-collision", True)
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

    cexpand = ['and']
    for i in range(0, rounds - 1):
        k = 'r' + str(i)
        if not k in in_obj:
            continue

        for i in range(0, len(in_obj[k]), ow):
            delta = in_obj[k][i:i+ow]
            pos = i*2
            print(pos)
            cexpand.append(hf.models.vars.differential(delta, 'h1' + k + 'i', pos, 'h2' + k + 'i', pos))
    cexpand = tuple(cexpand)
    hf.models.vars.write_clause('cexpand', cexpand, '56-expand.txt')


    ceinput = ['and']
    for i in range(0, len(in_obj['input']), ow):
        delta = in_obj['input'][i:i+ow]
        pos = i*2
        ceinput.append(hf.models.vars.differential(delta, 'h1in', pos, 'h2in', pos))
    ceinput = tuple(ceinput)
    #print(cexpand)
    hf.models.vars.write_clause('ceinput', ceinput, '58-einput.txt')

    hf.models.vars.write_assign(['ccollision', 'cinput', 'czero', 'cexpand', 'ceinput'])
    m.collapse()
    m.build()
    r = m.run(count=1)
    if r:
        for rs in m.results_generator(algo):
            obj = {}
            obj['w'] = w
            obj['rounds'] = rounds
            obj['input'] = hf.models.vars.compute_ddelta(rs['h1i'], rs['h2i'])[0:input_margin]
            for r in range(0, rounds):
                obj['r' + str(r)] = hf.models.vars.compute_ddelta(rs['h1r' + str(r) + 'i'], rs['h2r' + str(r) + 'i'])
            print(obj)

if __name__ == "__main__":
    __main__()
