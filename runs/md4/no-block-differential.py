#!/usr/bin/python3

import itertools

import cmsh

import hash_framework.algorithms as hfa
import hash_framework.utils as hfu

def find_differential(state_differential):
    with cmsh.Model() as model:
        model.solver.config_timeout(30)

        hf: hfa.md4 = hfa.resolve('md4')

        block_1 = model.vec(hf.block_size)
        block_2 = model.vec(hf.block_size)
        model.add_assert(block_1 == block_2)

        for round_index in range(0, hf.rounds):
            iv_1 = model.vec(hf.state_size)
            iv_1s = model.split_vec(iv_1, hf.int_size)
            iv_2 = model.vec(hf.state_size)
            iv_2s = model.split_vec(iv_2, hf.int_size)

            model.add_assert((iv_1s[0] ^ iv_2s[0]) == state_differential)

            for index, state_1 in enumerate(iv_1s[1:], start=1):
                model.add_assert(state_1 == iv_2s[index])

            output_1s, _ = hf.eval(model, block_1, iv=iv_1s, rounds=[round_index])
            output_2s, _ = hf.eval(model, block_2, iv=iv_2s, rounds=[round_index])

            output_1 = model.join_vec(output_1s)
            output_2 = model.join_vec(output_2s)

            model.add_assert(output_1 == output_2)

        sat = model.solve()
        if sat is True:
            print(f"{state_differential} - SAT")
        elif sat is None:
            print(f"{state_differential} - timeout")


def args_gen():
    for num_diff_bits in range(0, 33):
        for state_diffs in itertools.combinations(range(0, 32), num_diff_bits):
            differential = 0
            for bit in state_diffs:
                differential |= (1 << bit)
            yield (differential,)

def main():
    hfu.parallel_run(find_differential, args_gen)

if __name__ == "__main__":
    main()
