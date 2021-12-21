#!/usr/bin/python3

import multiprocessing

import cmsh
from hash_framework.algorithms import md4


def build_collision(differential_path, offset, rounds):
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

    model.add_assert((rounds_1 ^ rounds_2) == differential_path)

    if model.solve():
        print("SAT", offset)
        print(hex(int(block_1)))
        print(hex(int(block_2)))
        print(hex(int(output_1)))
        print(hex(int(block_1 ^ block_2)))
        print(hex(int(rounds_1 ^ rounds_2)))
    else:
        print("UNSAT", offset)


def main():
    rounds = 32
    pool = multiprocessing.Pool(processes=4)

    for i in range(0, rounds * 32):
        pool.apply_async(build_collision, args=(1 << i, i, rounds))

    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
