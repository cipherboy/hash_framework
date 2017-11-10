
def md4f(x, y, z):
    return hash_or(hash_and(x, y), hash_and(hash_not(x), z))

def md4g(x, y, z):
    return hash_or(hash_or(hash_and(x, y), hash_and(x, z)), hash_and(y, z))

def md4h(x, y, z):
    return hash_xor(hash_xor(x, y), z)

def md4apply32(func, x, y, z):
    result = []
    for i in range(0, 32):
        result.append(func(x[i], y[i], z[i]))
    return result

def md4f32(x, y, z):
    return md4apply32(md4f, x, y, z)

def md4g32(x, y, z):
    return md4apply32(md4g, x, y, z)

def md4h32(x, y, z):
    return md4apply32(md4h, x, y, z)

def md4round1a(a, b, c, d, x, l):
    return hash_rotl(hash_addl(hash_addl(a, md4f32(b, c, d)), x), l)

def md4round2a(a, b, c, d, x, l):
    return hash_rotl(hash_addl(hash_addl(hash_addl(a, hash_tobitl(0x5A827999)), md4g32(b, c, d)), x), l)

def md4round3a(a, b, c, d, x, l):
    return hash_rotl(hash_addl(hash_addl(hash_addl(a, hash_tobitl(0x6ED9EBA1)), md4h32(b, c, d)), x), l)

def md4applyround(shift, xchoice, ivc, state, file_out, eval_table, roundfunc, prefix=""):
    r = 0
    rc = 0
    xx = buildxx(xchoice[rc], eval_table, prefix=prefix)
    for i in range(0, len(xchoice) // 4):
        yy = roundfunc(state[0], state[1], state[2], state[3], xx, shift[r])
        r = (r + 1) % 4
        rc += 1
        ivc, eval_table = writeyy(file_out, prefix, yy, ivc, eval_table)
        xx = buildxx(xchoice[rc], eval_table, prefix=prefix)
        state[0] = replace_yy(ivc, eval_table, prefix=prefix)

        yy = roundfunc(state[3], state[0], state[1], state[2], xx, shift[r])
        r = (r + 1) % 4
        rc += 1
        ivc, eval_table = writeyy(file_out, prefix, yy, ivc, eval_table)
        xx = buildxx(xchoice[rc], eval_table, prefix=prefix)
        state[3] = replace_yy(ivc, eval_table, prefix=prefix)

        yy = roundfunc(state[2], state[3], state[0], state[1], xx, shift[r])
        r = (r + 1) % 4
        rc += 1
        ivc, eval_table = writeyy(file_out, prefix, yy, ivc, eval_table)
        xx = buildxx(xchoice[rc], eval_table, prefix=prefix)
        state[2] = replace_yy(ivc, eval_table, prefix=prefix)

        yy = roundfunc(state[1], state[2], state[3], state[0], xx, shift[r])
        r = (r + 1) % 4
        rc += 1
        ivc, eval_table = writeyy(file_out, prefix, yy, ivc, eval_table)
        xx = buildxx(xchoice[rc], eval_table, prefix=prefix)
        state[1] = replace_yy(ivc, eval_table, prefix=prefix)
    return ivc, eval_table, state

def md4_build_state(eval_table, prefix=""):
    state = [[], [], [], []]
    for i in range(0, 32):
        name = prefix + "s" + str(i)
        if name in eval_table:
            state[0].append(eval_table[name])
        else:
            state[0].append(name)
    for i in range(32, 64):
        name = prefix + "s" + str(i)
        if name in eval_table:
            state[1].append(eval_table[name])
        else:
            state[1].append(name)
    for i in range(64, 96):
        name = prefix + "s" + str(i)
        if name in eval_table:
            state[2].append(eval_table[name])
        else:
            state[2].append(name)
    for i in range(96, 128):
        name = prefix + "s" + str(i)
        if name in eval_table:
            state[3].append(eval_table[name])
        else:
            state[3].append(name)
    return state


def compute_md4(block, state=None, rounds=48):
    eval_table = BuildBlockEvalTable(block)

    if state == None:
        state = md4_build_state(eval_table)
    else:
        eval_table = MD4BuildBlockStateEvalTable(block, state)
        state = md4_build_state(eval_table)

    return perform_md4(eval_table, state, None, None, None, rounds=rounds)

def perform_md4(eval_table, original_state, f, f3, f2=None, prefix="", rounds=48):
    state = original_state[:]
    state[0] = original_state[0][:]
    state[1] = original_state[1][:]
    state[2] = original_state[2][:]
    state[3] = original_state[3][:]
    ic = 0

    shift = [3, 7, 11, 19]
    xchoice = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0]
    if rounds <= 16:
        xchoice = xchoice[:rounds] + [0]
    ic, eval_table, state = md4applyround(shift, xchoice, ic, state, f, eval_table, md4round1a, prefix=prefix)

    if rounds > 16:
        shift = [3, 5, 9, 13]
        xchoice = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15, 0]
        if rounds <= 32:
            xchoice = xchoice[:(rounds - 16)] + [0]
        ic, eval_table, state = md4applyround(shift, xchoice, ic, state, f, eval_table, md4round2a, prefix=prefix)

        if rounds > 32:
            shift = [3, 9, 11, 15]
            xchoice = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15, 0]
            if rounds <= 48:
                xchoice = xchoice[:(rounds - 32)] + [0]
            ic, eval_table, state = md4applyround(shift, xchoice, ic, state, f, eval_table, md4round3a, prefix=prefix)

    print(ic)
    if f != None:
        f.write("\n\n")
        f.flush()
        f.close()

    oaa = hash_addl(original_state[0], state[0])
    obb = hash_addl(original_state[1], state[1])
    occ = hash_addl(original_state[2], state[2])
    odd = hash_addl(original_state[3], state[3])

    print(hash_tonum(oaa))
    print(hash_tonum(obb))
    print(hash_tonum(occ))
    print(hash_tonum(odd))

    eval_table = writeo(f3, prefix, oaa, 'oaa', eval_table)
    eval_table = writeo(f3, prefix, obb, 'obb', eval_table)
    eval_table = writeo(f3, prefix, occ, 'occ', eval_table)
    eval_table = writeo(f3, prefix, odd, 'odd', eval_table)
    stats = []

    print("Generating stats...")
    for i in eval_table:
        stats.append(var_count(eval_table[i]))
    print(list(map(lambda x: (x, stats.count(x)), set(stats))))

    global clause_dedupe_s
    print("Deduplicated clauses: " + str(len(clause_dedupe_s)))
    for t in clause_dedupe_s:
        if len(prefix) > 0:
            if prefix == t[0:len(prefix)]:
                eval_table[t] = clause_dedupe_s[t]
        else:
            eval_table[t] = clause_dedupe_s[t]

    if f2 != None:
        for t in clause_dedupe_s:
            if len(prefix) > 0:
                if prefix == t[0:len(prefix)]:
                    f2.write(t + " := " + translate(clause_dedupe_s[t]) + ";\n")
            else:
                f2.write(t + " := " + translate(clause_dedupe_s[t]) + ";\n")


    if f3 != None:
        f3.write("\n\n")
        f3.flush()
        f3.close()

    return eval_table

class md4:
    def r1(a, b, c, d, x, l):
        return hash_rotl(hash_addl(hash_addl(a, md4f32(b, c, d)), x), l)

    def r2(a, b, c, d, x, l):
        return hash_rotl(hash_addl(hash_addl(hash_addl(a, hash_tobitl(0x5A827999)), md4g32(b, c, d)), x), l)

    def r3(a, b, c, d, x, l):
        return hash_rotl(hash_addl(hash_addl(hash_addl(a, hash_tobitl(0x6ED9EBA1)), md4h32(b, c, d)), x), l)

    default_state_bits = [
        ''.join(hash_tobitl(0x67452301)),
        ''.join(hash_tobitl(0xefcdab89)),
        ''.join(hash_tobitl(0x98badcfe)),
        ''.join(hash_tobitl(0x10325476))
    ]

    default_state = [
        0x67452301,
        0xefcdab89,
        0x98badcfe,
        0x10325476
    ]

    name = "md4"
    rounds = 48
    block_size = 512
    state_size = 128
    int_size = 32
    shifts = [3, 7, 11, 19]*4 + [3, 5, 9, 13]*4 + [3, 9, 11, 15]*4
    block_schedule = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] + [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15] + [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]
    block_map = {}
    round_funcs = []
    state_vars = ["s" + str(i) for i in range(0, 128)]
    block_vars = ["b" + str(i) for i in range(0, 512)]
    intermediate_vars = ["s" + str(i) for i in range(0, 32*48)]
    output_vars = ["oaa" + str(i) for i in range(0, 32)] + ["obb" + str(i) for i in range(0, 32)] + ["occ" + str(i) for i in range(0, 32)] + ["odd" + str(i) for i in range(0, 32)]

    generate_files = ["02-%s-md4-dedupe.txt", "03-%s-md4-intermediate.txt", "04-%s-md4-output.txt"]

    def evaluate(self, block, state, rounds=None):
        if rounds is None:
            rounds = self.rounds
        return compute_md4(block, state, rounds=rounds)

    def generate(self, prefixes=['h1', 'h2'], rounds=None):
        if rounds is None:
            rounds = self.rounds

        for prefix in prefixes:
            eval_table = EmptyEvalTable()
            state = md4_build_state(eval_table, prefix=prefix)

            f1 = open("03-" + prefix + "-md4-intermediate.txt", 'w')
            f2 = open("02-" + prefix + "-md4-dedupe.txt", 'w')
            f3 = open("04-" + prefix + "-md4-output.txt", 'w')
            perform_md4(eval_table, state, f1, f3, f2=f2, prefix=prefix, rounds=rounds)


    def __init__(self):
        rc = [md4.r1, md4.r2, md4.r3]
        self.round_funcs = [functools.partial(rc[i//16], l=self.shifts[i], x=["bs" + str(j) for j in range(self.block_schedule[i]*32, (self.block_schedule[i]+1)*32)]) for i in range(0, 48)]
        self.block_map = collections.defaultdict(list)
        for i in range(0, self.rounds):
            self.block_map[self.block_schedule[i]].append(i)


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
            iet[k] = hash_tonum(eval_table[k])
        oet = {}
        t = []
        for i in range(0, self.state_size//self.int_size):
            t.append(iet['s' + str(i)])
        oet['state'] = block_to_hex(t)
        t = []
        for i in range(0, self.block_size//self.int_size):
            t.append(iet['b' + str(i)])
        oet['block'] = block_to_hex(t)
        t = []
        for i in range(0, self.rounds):
            t.append(block_to_hex([iet['i' + str(i)]]))
        oet['intermediate'] = t
        t = []
        for i in range(0, self.state_size//self.int_size):
            t.append(iet['o' + str(i)])
        oet['output'] = block_to_hex(t)

        return oet
