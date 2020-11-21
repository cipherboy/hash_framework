import cmsh
import hash_framework.algorithms._mersenne as _mersenne


def test_mersenne_known_test_vectors():
    model = cmsh.Model()
    state = _mersenne.seed_rand(model, 1131464071)
    assert len(state) == 624
    assert int(state[0]) == 1131464071
    assert int(state[1]) == (69069 * int(state[0])) & 0xffffffff

    index = -1
    value, index = _mersenne.gen_rand_long(model, state, index)
    assert int(value) == 3720971106
    value, index = _mersenne.gen_rand_long(model, state, index)
    assert int(value) == 1185582179
    value, index = _mersenne.gen_rand_long(model, state, index)
    assert int(value) == 2564798321
    value, index = _mersenne.gen_rand_long(model, state, index)
    assert int(value) == 1931142078

def test_mersenne_reverse_seed():
    model = cmsh.Model()

    seed = model.vec(32)
    state = _mersenne.seed_rand(model, seed)

    index = -1
    expectations = [3720971106, 1185582179, 2564798321, 1931142078,
                    1922624258, 2775287020,  184205937,  612490464,
                    3208490327, 1665128171, 1140358085, 3611116024,
                     953884115, 4099552555, 2606495820,  685898173]

    for expected in expectations:
        value, index = _mersenne.gen_rand_long(model, state, index)
        model.add_assert(value == expected)

    assert model.solve()
    assert int(seed) == 1131464071
