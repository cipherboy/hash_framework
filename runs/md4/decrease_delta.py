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
    rfs = [_md4.md4r1, _md4.md4r2, _md4.md4r3]
    rshifts = [[3, 7, 11, 19], [3, 5, 9, 13], [3, 9, 11, 15]]

    # Input blocks
    xa, xb = mod.vec(32), mod.vec(32)
    x = xa ^ xb

    deltas = {}

    for rindex in range(0, 3):
        rfunc = rfs[rindex]

        for shift in rshifts[rindex]:
            existing_inputs = []
            for index in range(0, 20):
                key = (rindex, shift, index)

                # XORs
                x_a, x_b, x_c, x_d = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)

                # Inputs
                a1, a2, a3, a4 = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)
                b1, b2, b3, b4 = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)

                na = _md4.md4_round([xa], rfunc, [a1, a2, a3, a4], 0, shift)[1]
                nb = _md4.md4_round([xb], rfunc, [b1, b2, b3, b4], 0, shift)[1]

                # XORs of states
                old = a1 ^ b1
                x_b = a2 ^ b2
                x_c = a3 ^ b3
                x_d = a4 ^ b4
                new = na ^ nb

                for item in existing_inputs:
                    eold, enew = item
                    mod.add_assert(old != eold)
                    mod.add_assert(new != enew)
                existing_inputs.append((old, new))

                mod.add_assert(old != 0)
                mod.add_assert(x_b == 0)
                mod.add_assert(x_c == 0)
                mod.add_assert(x_d == 0)
                mod.add_assert(old.bit_sum() > new.bit_sum())
                if index < 10:
                    mod.add_assert(new.bit_sum() <= 5)

                deltas[key] = (old, new)

    mod.add_assert(x != 0)
    mod.add_assert(x.bit_sum() < 5)

    print("Solving...")
    sat = mod.solve()
    print(sat)
    while sat:
        print(bin(int(x)))

        for key in deltas:
            value = deltas[key]
            print(key, bin(int(value[0])), bin(int(value[1])))

        negated = mod.negate_solution(x)
        mod.add_assert(negated)
        sat = mod.solve()
        # sat = mod.solve()


if __name__ == "__main__":
    main()
