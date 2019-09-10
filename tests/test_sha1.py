import cmsh
from hash_framework.algorithms.sha1 import sha1


def gen_blocks(model, count, width):
    result = []
    for i in range(0, count):
        result.append(model.vec(width))
    return result


def split_hex(string, width=8):
    result = []
    for i in range(0, len(string), width):
        block = ""
        for j in range(0, width, 2):
            block = block + string[i + j : i + j + 2]
        result.append(int(block, 16))
    return result


def test_known_value():
    model = cmsh.Model()
    h = sha1()

    block_hex = "80000000" + ("0" * 120)
    block = list(map(lambda x: model.to_vector(x, width=32), split_hex(block_hex)))

    res_hex = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    res_known = list(map(lambda x: model.to_vector(x, width=32), split_hex(res_hex)))
    res, _ = h.compute(model, block)

    assert list(map(int, res_known)) == list(map(int, res))
