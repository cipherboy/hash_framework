import cmsh
from hash_framework.algorithms import _md4
from hash_framework.algorithms import md4

def gen_blocks(mod, count, width):
    result = mod.vec(count*width)
    return mod.split_vec(result, width)

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
    mod = cmsh.Model()

    k1 = "839c7a4d7a92cb5678a5d5b9eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edd45e51fe39708bf9427e9c3e8b9"
    k2 = "839c7a4d7a92cbd678a5d529eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edc45e51fe39708bf9427e9c3e8b9"

    known_shaped_1 = list(map(lambda x: mod.to_vector(x, width=32), split_hex(k1, 8)))
    known_shaped_2 = list(map(lambda x: mod.to_vector(x, width=32), split_hex(k2, 8)))
    known_result_shaped_1, known_rounds_shaped_1 = _md4.md4(mod, known_shaped_1)
    known_result_shaped_2, known_rounds_shaped_2 = _md4.md4(mod, known_shaped_2)

    known_1 = mod.join_vec(known_shaped_1)
    known_2 = mod.join_vec(known_shaped_2)
    known_result_1 = mod.join_vec(known_result_shaped_1)
    known_rounds_1 = mod.join_vec(known_rounds_shaped_1)
    known_result_2 = mod.join_vec(known_result_shaped_2)
    known_rounds_2 = mod.join_vec(known_rounds_shaped_2)

    block_1 = mod.vec(512)
    block_2 = mod.vec(512)
    block_shaped_1 = mod.split_vec(block_1, 32)
    block_shaped_2 = mod.split_vec(block_2, 32)

    result_shaped_1, rounds_shaped_1 = _md4.md4(mod, block_shaped_1)
    result_shaped_2, rounds_shaped_2 = _md4.md4(mod, block_shaped_2)

    result_1 = mod.join_vec(result_shaped_1)
    rounds_1 = mod.join_vec(rounds_shaped_1)
    result_2 = mod.join_vec(result_shaped_2)
    rounds_2 = mod.join_vec(rounds_shaped_2)

    mod.add_assert(block_1 != block_2)
    mod.add_assert(result_1 == result_2)
    dpath = (rounds_1 ^ rounds_2) == (known_rounds_1 ^ known_rounds_2)
    mod.add_assert(dpath)

    # for index, var in enumerate(block_1[:32]):
    #     mod.add_assume(var == known_1[index])
    # for index, var in enumerate(block_1[64:], 64):
    #     mod.add_assume(var == known_1[index])
    # for index, var in enumerate(block_2[:32]):
    #     mod.add_assume(var == known_2[index])
    # for index, var in enumerate(block_2[64:], 64):
    #     mod.add_assume(var == known_2[index])

    # mod.solve()

    # print(hex(int(block_1)) == hex(int(known_1)))
    # print(hex(int(block_2)) == hex(int(known_2)))

    # for index, var in enumerate(block_1[:32]):
    #     mod.remove_assume(var == known_1[index])
    # for index, var in enumerate(block_1[64:], 64):
    #     mod.remove_assume(var == known_1[index])
    # for index, var in enumerate(block_2[:32]):
    #     mod.remove_assume(var == known_2[index])
    # for index, var in enumerate(block_2[64:], 64):
    #     mod.remove_assume(var == known_2[index])

    # mod.remove_assume(dpath)
    # mod.add_assert((rounds_1[64:] ^ rounds_2[64:]) == (known_rounds_1[64:] ^ known_rounds_2[64:]))
    mod.add_assert((block_1 != known_1) | (block_2 != known_2) | (block_1 != known_2) | (block_2 != known_1))

    mod.solve()
    print(hex(int(block_1)))
    print(hex(int(block_2)))


if __name__ == "__main__":
    main()
