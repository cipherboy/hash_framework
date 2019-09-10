import hash_framework.algorithms._md5 as _md5
import functools, collections


class md5:
    def r1(a, b, c, d, x, l, t):
        return _md5.md5r1(a, b, c, d, x, l, t)

    def r2(a, b, c, d, x, l, t):
        return _md5.md5r2(a, b, c, d, x, l, t)

    def r3(a, b, c, d, x, l, t):
        return _md5.md5r3(a, b, c, d, x, l, t)

    def r4(a, b, c, d, x, l, t):
        return _md5.md5r4(a, b, c, d, x, l, t)

    default_state = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476]

    name = "md5"
    rounds = 64
    block_size = 512
    state_size = 128
    int_size = 32
    round_size = 32
    shifts = (
        [7, 12, 17, 22] * 4
        + [5, 9, 14, 20] * 4
        + [4, 11, 16, 23] * 4
        + [6, 10, 15, 21] * 4
    )
    block_schedule = (
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        + [1, 6, 11, 0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12]
        + [5, 8, 11, 14, 1, 4, 7, 10, 13, 0, 3, 6, 9, 12, 15, 2]
        + [0, 7, 14, 5, 12, 3, 10, 1, 8, 15, 6, 13, 4, 11, 2, 9]
    )
    constants = [
        0xD76AA478,
        0xE8C7B756,
        0x242070DB,
        0xC1BDCEEE,
        0xF57C0FAF,
        0x4787C62A,
        0xA8304613,
        0xFD469501,
        0x698098D8,
        0x8B44F7AF,
        0xFFFF5BB1,
        0x895CD7BE,
        0x6B901122,
        0xFD987193,
        0xA679438E,
        0x49B40821,
        0xF61E2562,
        0xC040B340,
        0x265E5A51,
        0xE9B6C7AA,
        0xD62F105D,
        0x02441453,
        0xD8A1E681,
        0xE7D3FBC8,
        0x21E1CDE6,
        0xC33707D6,
        0xF4D50D87,
        0x455A14ED,
        0xA9E3E905,
        0xFCEFA3F8,
        0x676F02D9,
        0x8D2A4C8A,
        0xFFFA3942,
        0x8771F681,
        0x6D9D6122,
        0xFDE5380C,
        0xA4BEEA44,
        0x4BDECFA9,
        0xF6BB4B60,
        0xBEBFBC70,
        0x289B7EC6,
        0xEAA127FA,
        0xD4EF3085,
        0x04881D05,
        0xD9D4D039,
        0xE6DB99E5,
        0x1FA27CF8,
        0xC4AC5665,
        0xF4292244,
        0x432AFF97,
        0xAB9423A7,
        0xFC93A039,
        0x655B59C3,
        0x8F0CCC92,
        0xFFEFF47D,
        0x85845DD1,
        0x6FA87E4F,
        0xFE2CE6E0,
        0xA3014314,
        0x4E0811A1,
        0xF7537E82,
        0xBD3AF235,
        0x2AD7D2BB,
        0xEB86D391,
    ]
    block_map = {}
    round_funcs = []

    def __init__(self):
        rc = [md5.r1, md5.r2, md5.r3, md5.r4]
        self.round_funcs = [
            functools.partial(rc[i // 16], l=self.shifts[i], t=self.constants[i])
            for i in range(0, 64)
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

    def compute(self, model, block, iv=None, rounds=None):
        if iv == None:
            iv = self.default_state[:]
        if rounds == None:
            rounds = self.rounds
        return _md5.md5(model, block, iv=iv, rounds=rounds)
