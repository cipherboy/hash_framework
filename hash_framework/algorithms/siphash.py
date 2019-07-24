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
    outlen = 8
    cROUNDS = 2
    dROUNDS = 4
    rounds = cROUNDS + dROUNDS
    key_size = 128
    state_size = 256
    int_size = 64
    block_map = {}
    round_funcs = []

    def __init__(self):
        self.round_func = _siphash.sipround

    def compute(self, model, key, block, iv=None, outlen=None, cROUNDS=None, dROUNDS=None):
        if iv == None:
            iv = self.default_state[:]
        if cROUNDS == None:
            cROUNDS = self.cROUNDS
        if dROUNDS == None:
            dROUNDS = self.dROUNDS
        if outlen == None:
            outlen = self.outlen
        return _siphash.siphash(model, key, block, v0=iv[0], v1=iv[1], v2=iv[2], v3=iv[3], outlen=outlen, cROUNDS=cROUNDS, dROUNDS=dROUNDS)