import random

def sipround(v0, v1, v2, v3):
    v0 = v0 + v1
    v1 = v1.rotl(13)
    v1 = v1 ^ v0
    v0 = v0.rotl(32)
    v2 = v2 + v3
    v3 = v3.rotl(16)
    v3 = v3 ^ v2
    v0 = v0 + v3
    v3 = v3.rotl(21)
    v3 = v3 ^ v0
    v2 = v2 + v1
    v1 = v1.rotl(17)
    v1 = v1 ^ v2
    v2 = v2.rotl(32)

    return v0, v1, v2, v3


def siphash(model, key, block, v0=0x736f6d6570736575, v1=0x646f72616e646f6d,
            v2=0x6c7967656e657261, v3=0x7465646279746573, outlen=8, cROUNDS=2,
            dROUNDS=4):
    assert len(key) == 128
    assert outlen in [8, 16]
    assert isinstance(cROUNDS, int)
    assert isinstance(dROUNDS, int)

    v0 = model.to_vector(v0, 64)
    v1 = model.to_vector(v1, 64)
    v2 = model.to_vector(v2, 64)
    v3 = model.to_vector(v3, 64)

    key_bytes = model.split_vec(key, 8)
    k0 = model.join_vec(reversed(key_bytes[0:8]))
    k1 = model.join_vec(reversed(key_bytes[8:16]))
    blocks = model.split_vec(block, 8)

    b = model.to_vector(len(blocks), 64)
    b = b.shiftl(56)

    v3 = v3 ^ k1
    v2 = v2 ^ k0
    v1 = v1 ^ k1
    v0 = v0 ^ k0

    if outlen == 16:
        v1 = v1 ^ 0xee

    range_max = len(blocks) - (len(blocks) % 8)
    print("range_max", range_max)
    for index in range(0, range_max, 8):
        print(index)
        m = reversed(blocks[index:index+8])
        m = model.join_vec(m)

        v3 = v3 ^ m

        for _ in range(0, cROUNDS):
            v0, v1, v2, v3 = sipround(v0, v1, v2, v3)

        v0 = v0 ^ m


    missing = [False, False, False, False, False, False, False, False] * (8 - (len(blocks) % 8))
    if len(missing) != 64:
        last_block = len(blocks) - (len(blocks) % 8)
        for block in reversed(blocks[last_block:]):
            for var in block:
                missing.append(var)

        assert len(missing) == 64
        missing = model.to_vector(missing)
        b = b | missing

    print("v0", hex(int(v0)))
    print("v1", hex(int(v1)))
    print("v2", hex(int(v2)))
    print("v3", hex(int(v3)))
    print("b", hex(int(b)))

    v3 = v3 ^ b

    for _ in range(0, cROUNDS):
        v0, v1, v2, v3 = sipround(v0, v1, v2, v3)

    v0 = v0 ^ b

    if outlen == 16:
        v2 = v2 ^ 0xee
    else:
        v2 = v2 ^ 0xff

    for _ in range(0, dROUNDS):
        v0, v1, v2, v3 = sipround(v0, v1, v2, v3)

    out = v0 ^ v1 ^ v2 ^ v3

    if outlen == 8:
        return out

    v1 = v1 ^ 0xdd

    for _ in range(0, dROUNDS):
        v0, v1, v2, v3 = sipround(v0, v1, v2, v3)

    out2 = v0 ^ v1 ^ v2 ^ v3

    return model.join_vec([out, out2])
