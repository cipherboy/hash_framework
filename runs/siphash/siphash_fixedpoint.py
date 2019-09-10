import cmsh
import hash_framework.algorithms._siphash as _siphash


def main():
    m = cmsh.Model()
    key = m.vec(128)

    r1 = _siphash.siphash(m, key, key, outlen=16, cROUNDS=1, dROUNDS=1)

    m.add_assert(r1 == key)
    assert m.solve()

    print(hex(int(key)))


if __name__ == "__main__":
    main()
