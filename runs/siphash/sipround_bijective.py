import cmsh
import hash_framework.algorithms._siphash as _siphash


def main():
    m = cmsh.Model()
    av0 = m.vec(64)
    av1 = m.vec(64)
    av2 = m.vec(64)
    av3 = m.vec(64)
    bv0 = m.vec(64)
    bv1 = m.vec(64)
    bv2 = m.vec(64)
    bv3 = m.vec(64)

    ar0, ar1, ar2, ar3 = _siphash.sipround(av0, av1, av2, av3)
    br0, br1, br2, br3 = _siphash.sipround(bv0, bv1, bv2, bv3)

    m.add_assert(ar0 == br0)
    m.add_assert(ar1 == br1)
    m.add_assert(ar2 == br2)
    m.add_assert(ar3 == br3)
    m.add_assert((av0 != bv0) | (av1 != bv1) | (av2 != bv2) | (av3 != bv3))

    sat = m.solve()
    assert not sat

    if sat:
        print(hex(int(av0)), hex(int(av1)), hex(int(av2)), hex(int(av3)))
        print(hex(int(bv0)), hex(int(bv1)), hex(int(bv2)), hex(int(bv3)))
        print(hex(int(ar0)), hex(int(ar1)), hex(int(ar2)), hex(int(ar3)))


if __name__ == "__main__":
    main()
