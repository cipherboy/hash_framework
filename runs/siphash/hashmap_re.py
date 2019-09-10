import random

import cmsh
import hash_framework.algorithms._siphash as _siphash


def main():
    m = cmsh.Model()
    cr = 1
    dr = 3
    num_points = 16
    m_bits = 4
    num_others = 128
    key_bits = 4
    guess_bits = 128

    print(cr, dr, num_points, m_bits, num_others, key_bits, guess_bits)

    known = random.randint(0, 1 << key_bits)
    if key_bits < 128:
        known_128 = m.join_vec([m.to_vec(known, key_bits), m.to_vec(0, 128 - key_bits)])
    else:
        known_128 = m.to_vec(known, 128)

    guess = m.vec(guess_bits)
    if guess_bits < 128:
        guess = m.join_vec([guess, m.to_vec(0, 128 - guess_bits)])

    values = [random.randint(0, 1 << 64) for i in range(0, num_points)]
    values_64 = [m.to_vec(values[i], 64) for i in range(0, num_points)]

    for i in range(0, num_points):
        for j in range(i + 1, num_points):
            k_i = _siphash.siphash(
                m, known_128, values_64[i], outlen=8, cROUNDS=cr, dROUNDS=dr
            )
            k_j = _siphash.siphash(
                m, known_128, values_64[j], outlen=8, cROUNDS=cr, dROUNDS=dr
            )

            g_i = _siphash.siphash(
                m, guess, values_64[i], outlen=8, cROUNDS=cr, dROUNDS=dr
            )
            g_j = _siphash.siphash(
                m, guess, values_64[j], outlen=8, cROUNDS=cr, dROUNDS=dr
            )

            if int(k_i[-m_bits:]) == int(k_j[-m_bits:]):
                m.add_assert(g_i[-m_bits:] == g_j[-m_bits:])
            else:
                m.add_assert(g_i[-m_bits:] != g_j[-m_bits:])

    print("Solving...")
    assert m.solve()

    print(hex(int(known_128)))
    print(hex(int(guess)))

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
