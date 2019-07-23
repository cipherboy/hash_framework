import hash_framework.algorithms._sha1 as _sha1
import functools, collections

class sha1:
    default_state = [
        0x67452301,
        0xEFCDAB89,
        0x98BADCFE,
        0x10325476,
        0xC3D2E1F0
    ]

    name = "md5"
    rounds = 80
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
