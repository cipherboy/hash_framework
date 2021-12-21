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

def test_mersenne_double_seed():
    model = cmsh.Model()
    left_seed = model.vec(32)
    left_state = _mersenne.seed_rand(model, left_seed)
    left_index = -1

    right_seed = model.vec(32)
    right_state = _mersenne.seed_rand(model, right_seed)
    right_index = -1

    model.add_assert(left_seed != right_seed)

    left_value, left_index = _mersenne.gen_rand_long(model, left_state, left_index)
    right_value, right_index = _mersenne.gen_rand_long(model, right_state, right_index)
    model.add_assert(left_value == right_value)

    left_value, left_index = _mersenne.gen_rand_long(model, left_state, left_index)
    right_value, right_index = _mersenne.gen_rand_long(model, right_state, right_index)
    model.add_assert(left_value == right_value)

    assert model.solve()
    assert int(left_seed) == int(right_seed)
