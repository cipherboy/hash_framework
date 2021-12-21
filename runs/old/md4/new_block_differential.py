import cmsh
from hash_framework.algorithms import _md4
from hash_framework.algorithms import md4


def gen_blocks(mod, count, width):
    result = mod.vec(count * width)
    return mod.split_vec(result, width)


def split_hex(string, width=8):
    result = []
    for i in range(0, len(string), width):
        # Reverse each group of two within each block
        block = ""
        for j in range(0, width, 2):
            block = string[i + j : i + j + 2] + block
        result.append(int(block, 16))
    return result


def main():
    mod = cmsh.Model()

    k1 = "839c7a4d7a92cb5678a5d5b9eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edd45e51fe39708bf9427e9c3e8b9"
    k2 = "839c7a4d7a92cbd678a5d529eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edc45e51fe39708bf9427e9c3e8b9"

    index = 1
    blocks_value_1 = list(map(lambda x: mod.to_vector(x, width=32), split_hex(k1, 8)))
    blocks_value_2 = list(map(lambda x: mod.to_vector(x, width=32), split_hex(k2, 8)))

    r_value_1, r_rounds_1 = _md4.md4(mod, blocks_value_1)
    r_value_2, r_rounds_2 = _md4.md4(mod, blocks_value_2)

    assert r_rounds_1[0] == r_rounds_2[0]
    a, b, c, d = (
        r_rounds_1[0],
        md4.md4.default_state[1],
        md4.md4.default_state[2],
        md4.md4.default_state[3],
    )
    x_a, x_b, x_c, x_d = 0, 0, 0, 0
    new_d_1, new_d_2 = r_rounds_1[1], r_rounds_2[1]
    x_new_d = new_d_1 ^ new_d_2
    assert new_d_1 != new_d_2

    # abcd
    # dabc
    new_x_1, new_x_2 = mod.vec(32), mod.vec(32)
    i_a, i_b, i_c, i_d = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)
    j_a, j_b, j_c, j_d = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)
    l_out_1 = _md4.md4_round([new_x_1], _md4.md4r1, [i_d, i_a, i_b, i_c], 0, 7)[1]
    l_out_2 = _md4.md4_round([new_x_2], _md4.md4r1, [j_d, j_a, j_b, j_c], 0, 7)[1]

    mod.add_assert(new_x_1 < new_x_2)
    mod.add_assert(i_a == j_a)
    mod.add_assert(i_b == j_b)
    mod.add_assert(i_c == j_c)
    mod.add_assert(i_d == j_d)
    mod.add_assert((l_out_1 ^ l_out_2) == (x_new_d))
    sat = mod.solve()
    assert sat
    while sat:
        print(
            bin(int(i_a) ^ int(j_a)),
            bin(int(new_x_1) ^ int(new_x_2)),
            bin(int(x_new_d)),
        )
        negated = mod.negate_solution(new_x_1 ^ new_x_2)

        mod.add_assert(negated)
        sat = mod.solve()


if __name__ == "__main__":
    main()
