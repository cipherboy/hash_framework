from hash_framework.algorithms._md5 import *
import functools, collections

class md5:
    def r1(a, b, c, d, x, t, l):
        return b_addl(b, b_rotl(b_addl(b_addl(md5f32(b, c, d), a), b_addl(x, b_tobitl(t))), l))

    def r2(a, b, c, d, x, t, l):
        return b_addl(b, b_rotl(b_addl(b_addl(md5g32(b, c, d), a), b_addl(x, b_tobitl(t))), l))

    def r3(a, b, c, d, x, t, l):
        return b_addl(b, b_rotl(b_addl(b_addl(md5h32(b, c, d), a), b_addl(x, b_tobitl(t))), l))

    def r4(a, b, c, d, x, t, l):
        return b_addl(b, b_rotl(b_addl(b_addl(md5i32(b, c, d), a), b_addl(x, b_tobitl(t))), l))

    default_state_bits = [
        ''.join(b_tobitl(0x67452301)),
        ''.join(b_tobitl(0xefcdab89)),
        ''.join(b_tobitl(0x98badcfe)),
        ''.join(b_tobitl(0x10325476))
    ]

    default_state = [
        0x67452301,
        0xefcdab89,
        0x98badcfe,
        0x10325476
    ]

    name = "md5"
    rounds = 64
    block_size = 512
    state_size = 128
    int_size = 32
    shifts = [7, 12, 17, 22]*4 + [5, 9, 14, 20]*4 + [4, 11, 16, 23]*4 + [6, 10, 15, 21]*4
    block_schedule = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] + [1, 6, 11, 0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12] + [5, 8, 11, 14, 1, 4, 7, 10, 13, 0, 3, 6, 9, 12, 15, 2] + [0, 7, 14, 5, 12, 3, 10, 1, 8, 15, 6, 13, 4, 11, 2, 9]
    block_map = {}
    round_funcs = []
    state_vars = ["s" + str(i) for i in range(0, 128)]
    block_vars = ["b" + str(i) for i in range(0, 512)]
    intermediate_vars = ["s" + str(i) for i in range(0, 32*64)]
    output_vars = ["oaa" + str(i) for i in range(0, 32)] + ["obb" + str(i) for i in range(0, 32)] + ["occ" + str(i) for i in range(0, 32)] + ["odd" + str(i) for i in range(0, 32)]

    generate_files = ["02-%s-md5-dedupe.txt", "03-%s-md5-intermediate.txt", "04-%s-md5-output.txt"]

    def __init__(self):
        # Round Functions not currently used
        #rc = [md4.r1, md4.r2, md4.r3]
        #self.round_funcs = [functools.partial(rc[i//16], l=self.shifts[i], x=["bs" + str(j) for j in range(self.block_schedule[i]*32, (self.block_schedule[i]+1)*32)]) for i in range(0, 48)]
        self.block_map = collections.defaultdict(list)
        for i in range(0, self.rounds):
            self.block_map[self.block_schedule[i]].append(i)

    def evaluate(self, block, state, rounds=None):
        if rounds is None:
            rounds = self.rounds
        return compute_md5(block, state, rounds=rounds)

    def generate(self, prefixes=['h1', 'h2'], rounds=None):
        if rounds is None:
            rounds = self.rounds

        for prefix in prefixes:
            eval_table = {}
            state = md5_build_state(eval_table, prefix=prefix)

            f1 = open("03-" + prefix + "-md5-intermediate.txt", 'w')
            f2 = open("02-" + prefix + "-md5-dedupe.txt", 'w')
            f3 = open("04-" + prefix + "-md5-output.txt", 'w')
            perform_md5(eval_table, state, f1, f3, f2=f2, prefix=prefix, rounds=rounds)

    def block_schedule_mapping(self):
        s = ['and']
        for i in range(0, self.block_size):
            s.append(('equal', 'bs' + str(i), 'b' + str(i)))
        return tuple(s)

    def sanitize(self, eval_table):
        et = {}
        for i in range(0, self.state_size//self.int_size):
            k = "s" + str(i)
            v = []
            for j in range(i*self.int_size, (i+1)*self.int_size):
                v.append(eval_table['s' + str(j)])
            et[k] = ''.join(v)
        for i in range(0, self.block_size//self.int_size):
            k = "b" + str(i)
            v = []
            for j in range(i*self.int_size, (i+1)*self.int_size):
                v.append(eval_table['b' + str(j)])
            et[k] = ''.join(v)
        for i in range(0, self.rounds):
            k = "i" + str(i)
            v = []
            for j in range(i*self.int_size, (i+1)*self.int_size):
                v.append(eval_table['i' + str(j)])
            et[k] = ''.join(v)
        output_mapping = ["oaa", "obb", "occ", "odd"]
        for i in range(0, self.state_size//self.int_size):
            k = "o" + str(i)
            v = []
            for j in range(0, self.int_size):
                v.append(eval_table[output_mapping[i] + str(j)])
            et[k] = ''.join(v)
        return et

    def to_hex(self, eval_table):
        iet = {}
        for k in eval_table:
            iet[k] = b_tonum(eval_table[k])
        oet = {}
        t = []
        for i in range(0, self.state_size//self.int_size):
            t.append(iet['s' + str(i)])
        oet['state'] = b_block_to_hex(t)
        t = []
        for i in range(0, self.block_size//self.int_size):
            t.append(iet['b' + str(i)])
        oet['block'] = b_block_to_hex(t)
        t = []
        for i in range(0, self.rounds):
            t.append(b_block_to_hex([iet['i' + str(i)]]))
        oet['intermediate'] = t
        t = []
        for i in range(0, self.state_size//self.int_size):
            t.append(iet['o' + str(i)])
        oet['output'] = b_block_to_hex(t)

        return oet
