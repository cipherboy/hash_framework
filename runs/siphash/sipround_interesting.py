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
    av = m.join_vec([av0, av1, av2, av3])
    bv = m.join_vec([bv0, bv1, bv2, bv3])

    ar0, ar1, ar2, ar3 = _siphash.sipround(av0, av1, av2, av3)
    br0, br1, br2, br3 = _siphash.sipround(bv0, bv1, bv2, bv3)
    ar = m.join_vec([ar0, ar1, ar2, ar3])
    br = m.join_vec([br0, br1, br2, br3])

    eqv = m.to_vec([av[i] == bv[i] for i in range(0, len(av))])
    m.add_assert(eqv.bit_sum() == 255)

    eqr = m.to_vec([ar[i] == br[i] for i in range(0, len(ar))])
    m.add_assert(eqr.bit_sum() == 250)

    sat = m.solve()
    # assert not sat

    if sat:
        print(hex(int(av)))
        print(hex(int(bv)))
        print(hex(int(ar)))
        print(hex(int(br)))


if __name__ == "__main__":
    main()
