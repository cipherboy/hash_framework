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
            block = string[i+j:i+j+2] + block
        result.append(int(block, 16))
    return result

def test_known_value():
    model = cmsh.Model()
    hf = siphash()

    key = model.to_vec(0x00, 128)
    block = []
    assert int(hf.compute(model, key, block)) == 0x1e924b9d737700d7

    key = model.to_vec(0x000102030405060708090a0b0c0d0e0f, 128)
    block = model.to_vec(0x000102030405060708090a0b0c0d0e, 120)
    assert int(hf.compute(model, key, block)) == 0xa129ca6149be45e5

    key = model.to_vec(0x00, 128)
    block = model.to_vec(0x48656c6c6f20776f726c64, 88)
    assert int(hf.compute(model, key, block)) == 0xc9e8a3021f3822d9

    key = model.to_vec(0x00, 128)
    block = model.to_vec(0x3132333435363738313233, 88)
    assert int(hf.compute(model, key, block)) == 0xf95d77ccdb0649f
