#!/usr/bin/python3

import itertools
import multiprocessing

import cmsh
from hash_framework.algorithms import md4

def build_collision(locations, rounds):
    model = cmsh.Model()
    hf = md4.md4()
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
        if r_index in locations:
            model.add_assert((rounds_1s[r_index] ^ rounds_2s[r_index]) != 0)
        else:
            model.add_assert((rounds_1s[r_index] ^ rounds_2s[r_index]) == 0)

    if model.solve():
        print("SAT", locations, rounds)
    else:
        print("UNSAT", locations, rounds)

    model.cleanup()


def main():
    rounds = 16

    pool = multiprocessing.Pool(processes=4)

    for rounds in range(16, 33, 4):
        for fs in range(1, rounds):
            for family in itertools.permutations(range(0, rounds-4), fs):
                pool.apply_async(build_collision, args=(family, rounds))

    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
