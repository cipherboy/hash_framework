import cmsh
import hash_framework.algorithms.siphash as siphash


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
    hf = siphash()

    key = model.to_vec(0x00, 128)
    block = []
    assert int(hf.compute(model, key, block)) == 0x1E924B9D737700D7

    key = model.to_vec(0x000102030405060708090A0B0C0D0E0F, 128)
    block = model.to_vec(0x000102030405060708090A0B0C0D0E, 120)
    assert int(hf.compute(model, key, block)) == 0xA129CA6149BE45E5

    key = model.to_vec(0x00, 128)
    block = model.to_vec(0x48656C6C6F20776F726C64, 88)
    assert int(hf.compute(model, key, block)) == 0xC9E8A3021F3822D9

    key = model.to_vec(0x00, 128)
    block = model.to_vec(0x3132333435363738313233, 88)
    assert int(hf.compute(model, key, block)) == 0xF95D77CCDB0649F
