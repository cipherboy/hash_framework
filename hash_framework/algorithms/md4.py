import hash_framework.algorithms._md4 as _md4
import functools, collections

import cmsh
from hash_framework.algorithms.utils import reshape


class md4:
    def r1(a, b, c, d, x, l):
        return _md4.md4r1(a, b, c, d, x, l)

    def r2(a, b, c, d, x, l):
        return _md4.md4r2(a, b, c, d, x, l)

    def r3(a, b, c, d, x, l):
        return _md4.md4r3(a, b, c, d, x, l)

    default_state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476]

    name = "md4"
    rounds = 48
    block_size = 512
    blocks = 16
    state_size = 128
    int_size = 32
    round_size = 32
    shifts = (
          [3, 7, 11, 19] * 4
        + [3, 5,  9, 13] * 4
        + [3, 9, 11, 15] * 4
    )
    block_schedule = (
          [0, 1, 2,  3, 4,  5, 6,  7, 8, 9, 10, 11, 12, 13, 14, 15]
        + [0, 4, 8, 12, 1,  5, 9, 13, 2, 6, 10, 14,  3,  7, 11, 15]
        + [0, 8, 4, 12, 2, 10, 6, 14, 1, 9,  5, 13,  3, 11,  7, 15]
    )
    block_map = {}
    round_funcs = []

    def __init__(self):
        rc = [md4.r1, md4.r2, md4.r3]
        self.round_funcs = [
            functools.partial(rc[i // 16], l=self.shifts[i]) for i in range(0, 48)
        ]
        self.block_map = collections.defaultdict(list)
        for i in range(0, self.rounds):
            self.block_map[self.block_schedule[i]].append(i)

    def columns(self):
        cols = ["iv", "block"]
        for i in range(0, self.rounds):
            cols.append("round" + str(i))
        cols.append("result")
        return cols

    def type(self, column):
        if column in ('iv', 'result'):
            return 'hex|128'
        elif column == 'block':
            return 'hex|512'
        else:
            return 'hex|32'

    def format(self, model, prefix: str, block=None, iv=None, output=None, rounds=None):
        result = {}
        if block is not None:
            block = reshape(model, block, 1, 512)
            result[prefix + 'block'] = hex(int(block))[2:]

        if state is not None:
            state = reshape(model, iv, 1, 128)
            result[prefix + 'state'] = hex(int(state))[2:]

        if output is not None:
            output = reshape(model, output, 1, 128)
            result[prefix + 'state'] = hex(int(state))[2:]

        if rounds is not None:
            rounds = reshape(model, output, self.rounds, 32)
            for index, round_value in enumerate(rounds):
                result[prefix + f'round{index}'] = hex(int(round_value))[2:]

        return result

    def eval(self, model, block, iv=None, rounds=None):
        if rounds is None:
            rounds = self.rounds
        if isinstance(rounds, int):
            rounds = range(0, rounds)
        if iv is None:
            iv = self.default_state[:]

        block = reshape(model, block, 16, 32)
        state = reshape(model, iv[:], 4, 32)
        intermediate = []

        for r_index in rounds:
            a, b, c, d = state
            element = block[self.block_schedule[r_index]]
            new_a = self.round_funcs[r_index](a, b, c, d, element)
            intermediate.append(new_a)
            state = d, new_a, b, c

        return state, intermediate

    def compute(self, model, block, iv=None, rounds=None):
        if iv is None:
            iv = self.default_state[:]
        if rounds is None:
            rounds = self.rounds
        return _md4.md4(model, block, iv=iv, rounds=rounds)
