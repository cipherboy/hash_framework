import cmsh
from hash_framework.algorithms.md4 import md4


def gen_blocks(model, count, width):
    result = []
    for i in range(0, count):
        result.append(model.vec(width))
    return result


def split_hex(string, width=8):
    result = []
    for i in range(0, len(string), width):
        # Reverse each group of two within each block
        block = ""
        for j in range(0, width, 2):
            block = string[i + j : i + j + 2] + block
        result.append(int(block, 16))
    return result


def test_known_value():
    model = cmsh.Model()
    h = md4()

    block_hex = "8" + ("0" * 127)
    block = list(map(lambda x: model.to_vector(x, width=32), split_hex(block_hex)))

    res_hex = "31d6cfe0d16ae931b73c59d7e0c089c0"
    res_known = list(map(lambda x: model.to_vector(x, width=32), split_hex(res_hex)))
    res, _ = h.compute(model, block)

    assert list(map(int, res_known)) == list(map(int, res))


def test_md4_known_collision():
    model = cmsh.Model()
    h = md4()

    k1 = "839c7a4d7a92cb5678a5d5b9eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edd45e51fe39708bf9427e9c3e8b9"
    k2 = "839c7a4d7a92cbd678a5d529eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edc45e51fe39708bf9427e9c3e8b9"
    blocks_1 = list(map(lambda x: model.to_vector(x, width=32), split_hex(k1, 8)))
    blocks_2 = list(map(lambda x: model.to_vector(x, width=32), split_hex(k2, 8)))

    assert list(map(int, blocks_1)) != list(map(int, blocks_2))
    assert len(blocks_1) == 16
    assert len(blocks_2) == 16

    res_1, _ = h.compute(model, blocks_1)
    res_2, _ = h.compute(model, blocks_2)
    assert list(map(int, res_1)) == list(map(int, res_2))


def test_md4_find_existing_collision():
    model = cmsh.Model()
    h = md4()

    k1 = "839c7a4d7a92cb5678a5d5b9eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edd45e51fe39708bf9427e9c3e8b9"
    k2 = "839c7a4d7a92cbd678a5d529eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edc45e51fe39708bf9427e9c3e8b9"
    blocks_value_1 = list(map(lambda x: model.to_vector(x, width=32), split_hex(k1, 8)))
    blocks_value_2 = list(map(lambda x: model.to_vector(x, width=32), split_hex(k2, 8)))

    indices = []
    for i in range(0, len(blocks_value_1)):
        if blocks_value_1[i] != blocks_value_2[i]:
            indices.append(i)

    r_value_1, r_rounds_1 = h.compute(model, blocks_value_1)
    r_value_2, r_rounds_2 = h.compute(model, blocks_value_2)

    blocks_1 = gen_blocks(model, 16, 32)
    blocks_2 = gen_blocks(model, 16, 32)

    # The blocks must differ...
    different_blocks = blocks_1[0] != blocks_2[0]
    for i in range(1, len(blocks_1)):
        different_blocks = different_blocks | (blocks_1[i] != blocks_2[i])
    model.add_assert(different_blocks)

    for i in range(0, len(blocks_1)):
        if i not in indices:
            model.add_assert(blocks_1[i] == blocks_value_1[i])
        model.add_assert(blocks_2[i] == blocks_value_2[i])

    # But their MD4s must be the same
    result_1, rounds_1 = h.compute(model, blocks_1)
    result_2, rounds_2 = h.compute(model, blocks_2)

    for i in range(0, 4):
        model.add_assert(result_2[i] == result_2[i])

    for i in range(0, len(rounds_1)):
        r_differential = r_rounds_1[i] ^ r_rounds_2[i]
        differential = rounds_1[i] ^ rounds_2[i]

        model.add_assert(differential == r_differential)

    assert model.solve()
    variables = []
    for index in indices:
        assert int(blocks_1[index]) == int(blocks_value_1[index])
        assert int(blocks_1[index] != blocks_2[index])
        variables.extend(blocks_1[index])

    new_solution = model.negate_solution(variables)
    model.add_assert(new_solution)

    assert not model.solve()


def test_md4_find_ivs():
    model = cmsh.Model()
    h = md4()

    k1 = "839c7a4d7a92cb5678a5d5b9eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edd45e51fe39708bf9427e9c3e8b9"
    k2 = "839c7a4d7a92cbd678a5d529eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edc45e51fe39708bf9427e9c3e8b9"

    blocks_value_1 = list(map(lambda x: model.to_vector(x, width=32), split_hex(k1, 8)))
    blocks_value_2 = list(map(lambda x: model.to_vector(x, width=32), split_hex(k2, 8)))

    bv1 = model.join_vec(blocks_value_1)
    bv2 = model.join_vec(blocks_value_2)

    r_value_1, r_rounds_1 = h.compute(model, blocks_value_1)
    r_value_2, r_rounds_2 = h.compute(model, blocks_value_2)
    rv1 = model.join_vec(r_value_1)
    rsv1 = model.join_vec(r_rounds_1)

    blocks_1 = gen_blocks(model, 16, 32)
    blocks_2 = gen_blocks(model, 16, 32)
    b1 = model.join_vec(blocks_1)
    b2 = model.join_vec(blocks_2)

    iv_1_arr = gen_blocks(model, 4, 32)
    iv_2_arr = gen_blocks(model, 4, 32)
    iv_1 = model.join_vec(iv_1_arr)
    iv_2 = model.join_vec(iv_2_arr)

    # The blocks must differ...
    model.add_assert(b1 == bv1)
    model.add_assert(b2 == bv2)

    # But their MD4s must be the same
    result_1_arr, rounds_1_arr = h.compute(model, blocks_1, iv=iv_1_arr)
    result_2_arr, rounds_2_arr = h.compute(model, blocks_2, iv=iv_2_arr)

    result_1 = model.join_vec(result_1_arr)
    rounds_1 = model.join_vec(rounds_1_arr)
    result_2 = model.join_vec(result_2_arr)
    rounds_2 = model.join_vec(rounds_2_arr)

    model.add_assert(iv_1 == iv_2)
    model.add_assert(result_1 == rv1)
    model.add_assert(rounds_1 == rsv1)
    model.add_assert(result_1 == result_2)

    rr1 = model.join_vec(r_rounds_1)
    rr2 = model.join_vec(r_rounds_2)

    real_diff_path = rr1 ^ rr2
    differential = rounds_1 ^ rounds_2

    diff_path = differential == real_diff_path

    model.add_assume(diff_path)
    assert model.solve()
