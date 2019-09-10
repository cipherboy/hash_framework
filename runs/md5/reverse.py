#!/usr/bin/python3

import itertools
import multiprocessing

import cmsh

from hash_framework.algorithms import md5
import hash_framework.utils as hfu


def main():
    model = cmsh.Model()
    hf = md5()

    block_1 = model.vec(512)
    block_1s = model.split_vec(block_1, 32)

    output_1s, rounds_1s = hf.compute(model, block_1s)
    output_1 = model.join_vec(output_1s)
    rounds_1 = model.join_vec(rounds_1s)

    model.add_assert(block_1[0:32].bit_sum() == 4)
    model.add_assert(block_1[32:] == 0)
    model.add_assert(output_1 == 0xD41D8CD98F00B204E9800998ECF8427E)

    print("Solving...")
    if model.solve():
        print("SAT", int(block_1))
    else:
        print("UNSAT")

    model.cleanup()


if __name__ == "__main__":
    main()
