import cmsh
from .utils import reshape

UPPER_MASK = 0x80000000
LOWER_MASK = 0x7fffffff
TEMPERING_MASK_B = 0x9d2c5680
TEMPERING_MASK_C = 0xefc60000

STATE_VECTOR_LENGTH = 624
STATE_VECTOR_M = 397

def seed_rand(model, seed):
    state = []
    state.append(model.to_vec(seed, 32))

    constant = model.to_vec(69069, 32)
    for index in range(1, STATE_VECTOR_LENGTH):
        state.append(
            model.to_vec(constant * state[index - 1], 32)
        )

        assert len(state[-1]) == 32

    assert len(state) == STATE_VECTOR_LENGTH

    return state

def gen_rand_long(model, state, index=-1):
    if index >= STATE_VECTOR_LENGTH or index < 0:
        magic = model.to_vec(0x9908b0df, 32)
        for state_index in range(0, STATE_VECTOR_LENGTH):
            y = state[state_index] & model.to_vec(UPPER_MASK, 32)
            y |= state[(state_index + 1) % STATE_VECTOR_LENGTH] & model.to_vec(LOWER_MASK, 32)

            next_value = y.shiftr(1, False)
            next_value ^= state[(state_index + STATE_VECTOR_M) % STATE_VECTOR_LENGTH]
            next_value ^= magic.splat_and(y.odd())

            state[state_index] = next_value

        index = 0

    y = state[index]
    y ^= y.shiftr(11, False)
    y ^= (y.shiftl(7) & model.to_vec(TEMPERING_MASK_B, 32))
    y ^= (y.shiftl(15) & model.to_vec(TEMPERING_MASK_C, 32))
    y ^= y.shiftr(18, False)

    index += 1
    return y, index
