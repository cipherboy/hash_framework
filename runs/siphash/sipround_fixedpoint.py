import cmsh
import hash_framework.algorithms._siphash as _siphash


def main():
    m = cmsh.Model()
    v0 = m.vec(64)
    v1 = m.vec(64)
    v2 = m.vec(64)
    v3 = m.vec(64)

    r0, r1, r2, r3 = _siphash.sipround(v0, v1, v2, v3)

    m.add_assert(v0 == r0)
    m.add_assert(v1 == r1)
    m.add_assert(v2 == r2)
    m.add_assert(v3 == r3)

    sat = m.solve()
    assert sat

    while sat:
        print(hex(int(v0)), hex(int(v1)), hex(int(v2)), hex(int(v3)))
        joined = m.join_vec([v0, v1, v2, v3])
        negated = m.negate_solution(joined)
        m.add_assert(negated)
        sat = m.solve()


if __name__ == "__main__":
    main()
