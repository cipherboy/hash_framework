import cmsh
import hash_framework.algorithms as hfa
import hash_framework.utils as hfu

import itertools

def model(differential=[]):
    model = cmsh.Model()
    hf = hfa.md4()

    rounds = range(48 - 24, 48)
    iv_1 = model.vec(128)
    iv_2 = model.vec(128)
    block_1 = model.vec(512)
    block_1s = model.split_vec(block_1, 32)
    block_2 = model.vec(512)
    block_2s = model.split_vec(block_2, 32)

    output_1s, rounds_1s = hf.eval(model, block_1, iv_1, rounds)
    output_1 = model.join_vec(output_1s)

    output_2s, rounds_2s = hf.eval(model, block_2, iv_2, rounds)
    output_2 = model.join_vec(output_2s)

    for index in differential:
        model.add_assert(rounds_1s[index] == rounds_2s[index])

    model.add_assert(output_1 == output_2)
    model.add_assert(block_1 < block_2)
    model.add_assert(iv_1 == iv_2)

    for i in range(48-4, 48):
        bi = hf.block_schedule[i]
        model.add_assert(block_1s[bi] == block_2s[bi])

    if model.solve():
        print(hex(int(iv_1)), hex(int(block_1)), hex(int(output_1)))
        print(hex(int(iv_2)), hex(int(block_2)), hex(int(output_2)))
        dif = []
        for index, element_1 in enumerate(block_1s):
            element_2 = block_2s[index]
            dif.append(hex(int(element_1) ^ int(element_2)))
        print(dif)
        dif = []
        dc = 0
        for index, element_1 in enumerate(rounds_1s):
            element_2 = rounds_2s[index]
            if int(element_1) != int(element_2):
                dc += 1
            dif.append(hex(int(element_1) ^ int(element_2)))
        print(dif, len(dif), dc)

def args_gen():
    for i in range(16, 12, -1):
        for indices in itertools.combinations(range(0, 16), i):
            yield (indices,)

def main():
    hfu.parallel_run(model, args_gen)

main()
