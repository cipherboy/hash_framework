import random

import cmsh
import hash_framework.algorithms._siphash as _siphash


def main():
    # m = cmsh.Model(cnf_mode=3)
    m = cmsh.Model()
    cr = 1
    dr = 1
    num_values = 4
    m_bits = 4
    max_delta = 0
    num_others = 128

    key_bits = 128

    print(cr, dr, num_values, m_bits, max_delta, num_others, key_bits)

    known = 0
    # known = random.randint(0, 1 << key_bits)
    if key_bits < 128:
        known_128 = m.join_vec([m.to_vec(known, key_bits), m.to_vec(0, 128 - key_bits)])
    else:
        known_128 = m.to_vec(known, 128)
    print(bin(known).count("0"))

    guess = m.vec(128)

    values = list(range(0, num_values))
    # values = [random.randint(0, 1 << 64) for i in range(0, num_values)]
    values_64 = [m.to_vec(values[i], 64) for i in range(0, num_values)]

    for value_64 in values_64:
        r_known = _siphash.siphash(
            m, known_128, value_64, outlen=8, cROUNDS=cr, dROUNDS=dr
        )
        r_guess = _siphash.siphash(m, guess, value_64, outlen=8, cROUNDS=cr, dROUNDS=dr)

        if max_delta == 0:
            m.add_assert(r_known[-m_bits:] == r_guess[-m_bits:])
        else:
            m.add_assert((r_known[-m_bits:] == r_guess[-m_bits:]).bit_sum <= max_delta)

    m.add_assert(known_128 != guess)
    assert m.solve()

    print(hex(int(known_128)))
    print(hex(int(guess)))
    print(bin(int(r_known[-m_bits:])))
    print(bin(int(r_guess[-m_bits:])))
    # return

    guess_value = m.to_vec(int(guess), 128)

    others = [random.randint(0, 1 << 64) for i in range(0, num_others)]
    rs_known = [
        _siphash.siphash(
            m, known_128, m.to_vec(others[i], 64), outlen=8, cROUNDS=cr, dROUNDS=dr
        )
        for i in range(0, num_others)
    ]
    rs_guess = [
        _siphash.siphash(
            m, guess_value, m.to_vec(others[i], 64), outlen=8, cROUNDS=cr, dROUNDS=dr
        )
        for i in range(0, num_others)
    ]

    print(
        len(
            list(
                filter(
                    lambda x: int(x[0][-m_bits:]) == int(x[1][-m_bits:]),
                    zip(rs_known, rs_guess),
                )
            )
        )
    )
    print(num_others)


if __name__ == "__main__":
    main()
