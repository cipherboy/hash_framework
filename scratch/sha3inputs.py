#!/usr/bin/env python3

import hash_framework as hf
import json, sys

used_inputs = set()

def is_double_expansion(inputs, b, ow, w):
    for idiff in inputs:
        bre = False
        for i in range(0, len(idiff), ow):
            delta = idiff[i:i+ow]
            pos = i*2
            if b[pos:pos+w] != 2*delta:
                bre = True
                break
        if bre:
            continue
        used_inputs.add(idiff)
        return True

    return False

def is_subset_expansion(inputs, b, ow, w):
    for idiff in inputs:
        bre = False
        for i in range(0, len(idiff), ow):
            delta = idiff[i:i+ow]
            pos = i*2
            if b[pos:pos+ow] != delta:
                bre = True
                break
        if bre:
            continue
        used_inputs.add(idiff)
        return True

    return False

def __main__():
    f = open('r1.txt', 'r').read().split('\n')[3:]
    inputs = set()

    for line in f:
        if len(line) < 2:
            continue
        obj = eval(line)
        inputs.add(obj['input'])

    print(len(inputs))
    print(len(f))


    algo = hf.algorithms.lookup('sha3')(w=2,rounds=1)

    m = hf.models()
    m.remote = False
    m.start("scratch-sha3-b50-r1-collision", False)
    n_inputs = set()
    count = 0
    double_expansions = 0
    subset_expansions = 0
    not_expansion = 0
    for rs in m.results_generator(algo):
        ci = hf.models.vars.compute_ddelta(rs['h1i'], rs['h2i'])[0:18]
        n_inputs.add(ci)
        count += 1

        if (count % (284397 // 100)) == 0:
            print(count)

    f = open('b50-r1-inputs.json', 'w')
    json.dump(list(n_inputs), f)
    if not f.closed:
        f.flush()
        f.close()

    n_inputs = set(json.load(open('b50-r1-inputs.json', 'r')))

    for ci in n_inputs:
        is_exp = False
        if is_double_expansion(inputs, ci, 1, 2):
            double_expansions += 1
            is_exp = True
        if is_subset_expansion(inputs, ci, 1, 2):
            subset_expansions += 1
            is_exp = True
        if not is_exp:
            not_expansion += 1


    print(double_expansions)
    print(subset_expansions)
    print(not_expansion)
    print(len(n_inputs))
    print(len(used_inputs))
    print(len(inputs))
    print(inputs.difference(used_inputs))
    print(count)



if __name__ == "__main__":
    __main__()
