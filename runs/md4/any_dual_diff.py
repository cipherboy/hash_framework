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
    shift = 3
    rfunc = _md4.md4r3

    # XORs are equal
    x_a, x_b, x_c, x_d = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)
    x_n = mod.vec(32)

    # State for instance group A
    aa1, aa2, aa3, aa4 = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)
    ab1, ab2, ab3, ab4 = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)

    # State for instance group B
    ba1, ba2, ba3, ba4 = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)
    bb1, bb2, bb3, bb4 = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)

    # All input blocks
    xaa, xab, xba, xbb = mod.vec(32), mod.vec(32), mod.vec(32), mod.vec(32)

    # Group A constraints
    naa = _md4.md4_round([xaa], rfunc, [aa1, aa2, aa3, aa4], 0, shift)[1]
    nab = _md4.md4_round([xab], rfunc, [ab1, ab2, ab3, ab4], 0, shift)[1]
    mod.add_assert((aa1 ^ ab1) == x_a)
    mod.add_assert((aa2 ^ ab2) == x_b)
    mod.add_assert((aa3 ^ ab3) == x_c)
    mod.add_assert((aa4 ^ ab4) == x_d)
    mod.add_assert((naa ^ nab) == x_n)

    # Group B constraints
    nba = _md4.md4_round([xba], rfunc, [ba1, ba2, ba3, ba4], 0, shift)[1]
    nbb = _md4.md4_round([xbb], rfunc, [bb1, bb2, bb3, bb4], 0, shift)[1]
    mod.add_assert((ba1 ^ bb1) == x_a)
    mod.add_assert((ba2 ^ bb2) == x_b)
    mod.add_assert((ba3 ^ bb3) == x_c)
    mod.add_assert((ba4 ^ bb4) == x_d)
    mod.add_assert((nba ^ nbb) == x_n)

    # Cross group constraints
    mod.add_assert(x_a == 0)
    mod.add_assert(x_b == 0)
    mod.add_assert(x_c == 0)
    mod.add_assert(x_d == 0)
    mod.add_assert((xaa ^ xab) != (xba ^ xbb))
    mod.add_assert((xaa ^ xab) <= (xba ^ xbb))
    mod.add_assert(xaa <= xab)
    mod.add_assert(xba <= xbb)
    mod.add_assert((naa ^ nab) == (nba ^ nbb))
    mod.add_assert((naa ^ nab).bit_sum() == 1)

    sat = mod.solve()
    while sat:
        ixa, ixb, ixc, ixd = int(x_a), int(x_b), int(x_c), int(x_d)
        ina, inb = int(naa ^ nab), int(nba ^ nbb)
        this_sol = [
            x_a == ixa,
            x_b == ixb,
            x_c == ixc,
            x_d == ixd,
            (naa ^ nab) == ina,
            (nba ^ nbb) == inb
        ]

        for constraint in this_sol:
            mod.add_assume(constraint)

        while sat:
            print(bin(int(xaa ^ xab)), bin(int(xba ^ xbb)), bin(ixa), bin(ixb), bin(ixc), bin(ixd), bin(ina), bin(inb))
            x_j = mod.join_vec([xaa ^ xab, xba ^ xbb])
            neg = mod.negate_solution(x_j)
            mod.add_assert(neg)
            sat = mod.solve()

        for constraint in this_sol:
            mod.remove_assume(constraint)
        mod.add_assert((naa ^ nab) != ina)
        mod.add_assert((nba ^ nbb) != inb)

        sat = mod.solve()



if __name__ == "__main__":
    main()
