#!/usr/bin/python3

import itertools
import multiprocessing

import cmsh

from hash_framework.algorithms import md4
import hash_framework.utils as hfu

def build_collision(family, rounds):
    model = cmsh.Model()
    hf = md4()
    hf.rounds = rounds

    block_1 = model.vec(512)
    block_1s = model.split_vec(block_1, 32)
    block_2 = model.vec(512)
    block_2s = model.split_vec(block_2, 32)

    output_1s, rounds_1s = hf.compute(model, block_1s)
    output_1 = model.join_vec(output_1s)
    rounds_1 = model.join_vec(rounds_1s)

    output_2s, rounds_2s = hf.compute(model, block_2s)
    output_2 = model.join_vec(output_2s)
    rounds_2 = model.join_vec(rounds_2s)

    model.add_assert(block_1 != block_2)
    model.add_assert(output_1 == output_2)

    assert len(rounds_1s) == rounds
    assert len(rounds_2s) == rounds

    for r_index in range(0, rounds):
        if r_index in family:
            model.add_assert((rounds_1s[r_index] ^ rounds_2s[r_index]) != 0)
        else:
            model.add_assert((rounds_1s[r_index] ^ rounds_2s[r_index]) == 0)

    if model.solve():
        print("SAT", family, rounds)
    else:
        print("UNSAT", family, rounds)

    model.cleanup()

def args_gen():
    for rounds in range(20, 33, 4):
        for fs in range(1, rounds//4):
            for family in itertools.combinations(range(0, rounds-4), fs):
                yield(family, rounds)

def main():
    hfu.parallel_run(build_collision, args_gen)

if __name__ == "__main__":
    main()
