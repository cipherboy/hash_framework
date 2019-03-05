import cmsh
from hash_framework.algorithms import _md4

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
            block = string[i+j:i+j+2] + block
        result.append(int(block, 16))
    return result

def main():
    model = cmsh.Model()

    k1 = "839c7a4d7a92cb5678a5d5b9eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edd45e51fe39708bf9427e9c3e8b9"
    k2 = "839c7a4d7a92cbd678a5d529eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edc45e51fe39708bf9427e9c3e8b9"

    blocks_value_1 = list(map(lambda x: model.to_vector(x, width=32), split_hex(k1, 8)))
    blocks_value_2 = list(map(lambda x: model.to_vector(x, width=32), split_hex(k2, 8)))

    bv1 = model.join_vec(blocks_value_1)
    bv2 = model.join_vec(blocks_value_2)

    r_value_1, r_rounds_1 = _md4.md4(model, blocks_value_1)
    r_value_2, r_rounds_2 = _md4.md4(model, blocks_value_2)

    blocks_1 = gen_blocks(model, 16, 32)
    blocks_2 = gen_blocks(model, 16, 32)

    b1 = model.join_vec(blocks_1)
    b2 = model.join_vec(blocks_2)

    iv_1_arr = gen_blocks(model, 4, 32)
    iv_2_arr = gen_blocks(model, 4, 32)
    iv_1 = model.join_vec(iv_1_arr)
    iv_2 = model.join_vec(iv_2_arr)

    # The blocks must differ...
    model.add_assert(b1 < b2)
    model.add_assert((b1 ^ b2) == (bv1 ^ bv2))

    # But their MD4s must be the same
    result_1_arr, rounds_1_arr = _md4.md4(model, blocks_1)
    result_2_arr, rounds_2_arr = _md4.md4(model, blocks_2)

    result_1 = model.join_vec(result_1_arr)
    rounds_1 = model.join_vec(rounds_1_arr)
    result_2 = model.join_vec(result_2_arr)
    rounds_2 = model.join_vec(rounds_2_arr)

    model.add_assert(iv_1 == iv_2)
    model.add_assert(result_1 == result_2)

    rr1 = model.join_vec(r_rounds_1)
    rr2 = model.join_vec(r_rounds_2)

    real_diff_path = rr1 ^ rr2
    differential = rounds_1 ^ rounds_2

    diff_path = differential == real_diff_path

    model.add_assume(diff_path)

    print(model.variables)
    print(len(model.clauses))

    assert model.solve()
    print(model.sat)

    solutions = []

    while len(solutions) < 32 and model.sat:
        left = (int(iv_1), int(b1))
        right = (int(iv_2), int(b2))

        print((left, right))

        real_diff_path = int(differential)
        solutions.append((left, right))

        try:
            model.remove_assume(diff_path)
            model.add_assert(differential != real_diff_path)
        except Exception as e:
            print(e)

        new_diff_path = (differential ^ real_diff_path).bit_sum() <= len(solutions)
        model.add_assume(new_diff_path)
        diff_path = new_diff_path

        model.solve()

    print(solutions)

if __name__ == "__main__":
    main()
