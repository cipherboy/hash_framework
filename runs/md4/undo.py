#!/usr/bin/python3

import itertools
import multiprocessing

import cmsh

from hash_framework.algorithms import md4
import hash_framework.utils as hfu


def main():
    model = cmsh.Model()
    hf = md4()

    iv_1 = model.vec(128)
    iv_2 = model.vec(128)

    block_1 = model.vec(512)
    block_2 = model.vec(512)

    output_1s, rounds_1s = hf.compute(model, block_1, iv=iv_1)
    output_1 = model.join_vec(output_1s)
    rounds_1 = model.join_vec(rounds_1s)

    output_2s, rounds_2s = hf.compute(model, block_2, iv=iv_2)
    output_2 = model.join_vec(output_2s)
    rounds_2 = model.join_vec(rounds_2s)

    model.add_assert(iv_1 != iv_2)
    model.add_assert(block_1 == 0)
    model.add_assert(block_2 == 0)
    model.add_assert(output_1 == output_2)

    if model.solve():
        print("SAT", int(iv_1), int(iv_2))
    else:
        print("UNSAT")

    model.cleanup()


if __name__ == "__main__":
    main()
