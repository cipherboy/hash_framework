import cmsh
from hash_framework.algorithms.md5 import md5


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
    h = md5()

    block_hex = "8" + ("0" * 127)
    block = list(map(lambda x: model.to_vector(x, width=32), split_hex(block_hex)))

    res_hex = "d41d8cd98f00b204e9800998ecf8427e"
    res_known = list(map(lambda x: model.to_vector(x, width=32), split_hex(res_hex)))
    res, _ = h.compute(model, block)

    assert list(map(int, res_known)) == list(map(int, res))
