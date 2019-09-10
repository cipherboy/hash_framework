import itertools

import cmsh
from hash_framework.algorithms.sha1 import sha1
import hash_framework.utils as hfu


def to_int(diff):
    result = 0
    for item in diff:
        result |= 1 << item
    return result


def collision(block_differentials, rounds):
    model = cmsh.Model()
    algo = sha1()

    block_1 = model.vec(512)
    block_1s = model.split_vec(block_1, 32)
    block_2 = model.vec(512)
    block_2s = model.split_vec(block_2, 32)

    b1w = algo.block_schedule(model, block_1s)
    w_1 = model.join_vec(b1w)
    b2w = algo.block_schedule(model, block_2s)
    w_2 = model.join_vec(b2w)

    output_1s, _ = algo.compute(model, block_1s, rounds=rounds)
    output_1 = model.join_vec(output_1s)
    output_2s, _ = algo.compute(model, block_2s, rounds=rounds)
    output_2 = model.join_vec(output_2s)

    model.add_assert((block_1 ^ block_2) == to_int(block_differentials))
    model.add_assert((output_1 ^ output_2) == 0)

    if model.solve():
        print(
            "SAT",
            block_differentials,
            hex(int(block_1)),
            hex(int(block_2)),
            hex(int(block_1 ^ block_2)),
            hex(int(output_1)),
        )
    else:
        print("UNSAT", block_differentials)


def args_gen():
    for i in range(1, 3):
        for item in itertools.combinations(range(0, 512), i):
            yield (item, 17)


def main():
    hfu.parallel_run(collision, args_gen)


if __name__ == "__main__":
    main()
