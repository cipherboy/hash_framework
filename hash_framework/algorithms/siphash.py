import hash_framework.algorithms._siphash as _siphash
import functools, collections

class siphash:
    default_state = [
        0x736f6d6570736575,
        0x646f72616e646f6d,
        0x6c7967656e657261,
        0x7465646279746573
    ]

    name = "siphash"
    cROUNDS = 2
    dROUNDS = 4
    rounds = cROUNDS + dROUNDS
    key_size = 128
    block_size = 512
    state_size = 160
    int_size = 32
    block_map = {}
    round_funcs = []

    def __init__(self):
        self.round_funcs = [
            functools.partial(_sha1.sha1_roundfunc, t=i)
            for i in range(0, 64)
        ]

    def compute(self, model, block, iv=None, rounds=None):
        if iv == None:
            iv = self.default_state[:]
        if rounds == None:
            rounds = self.rounds
        return _sha1.sha1(model, block, iv=iv, rounds=rounds)
