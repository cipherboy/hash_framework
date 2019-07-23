def md5f(x, y, z):
    return ((y ^ z) & x) ^ z

def md5g(x, y, z):
    return ((x ^ y) & z) ^ y

def md5h(x, y, z):
    return x ^ y ^ z

def md5i(x, y, z):
    return y ^ (x | ~z)

def md5r1(et, p, a, b, c, d, x, t, l):
    r = b_add4l(p, md5f32(b, c, d), a, x, b_tobitl(t))
    return b_addl(p, b, b_rotl(r, l)), et

def md5r2(et, p, a, b, c, d, x, t, l):
    r = b_add4l(p, md5g32(b, c, d), a, x, b_tobitl(t))
    return b_addl(p, b, b_rotl(r, l)), et

def md5r3(et, p, a, b, c, d, x, t, l):
    r = b_add4l(p, md5h32(b, c, d), a, x, b_tobitl(t))
    return b_addl(p, b, b_rotl(r, l)), et

def md5r4(et, p, a, b, c, d, x, t, l):
    r = b_add4l(p, md5i32(b, c, d), a, x, b_tobitl(t))
    return b_addl(p, b, b_rotl(r, l)), et

def md5applyround(shift, xchoice, ts, ivc, state, file_out, eval_table, roundfunc, prefix=""):
    r = 0
    rc = 0
    xx = buildxx(xchoice[rc], eval_table, prefix)
    for i in range(0, len(xchoice)//4):
        yy, et = roundfunc(eval_table, prefix, state[0], state[1], state[2], state[3], xx, ts[rc], shift[r])
        r = (r + 1) % 4
        rc += 1
        ivc, eval_table = writeyy(file_out, prefix, yy, ivc, eval_table)
        xx = buildxx(xchoice[rc], eval_table, prefix)
        state[0] = replace_yy(ivc, eval_table, prefix)

        yy, et = roundfunc(eval_table, prefix, state[3], state[0], state[1], state[2], xx, ts[rc], shift[r])
        r = (r + 1) % 4
        rc += 1
        ivc, eval_table = writeyy(file_out, prefix, yy, ivc, eval_table)
        xx = buildxx(xchoice[rc], eval_table, prefix)
        state[3] = replace_yy(ivc, eval_table, prefix)

        yy, et = roundfunc(eval_table, prefix, state[2], state[3], state[0], state[1], xx, ts[rc], shift[r])
        r = (r + 1) % 4
        rc += 1
        ivc, eval_table = writeyy(file_out, prefix, yy, ivc, eval_table)
        xx = buildxx(xchoice[rc], eval_table, prefix)
        state[2] = replace_yy(ivc, eval_table, prefix)

        yy, et = roundfunc(eval_table, prefix, state[1], state[2], state[3], state[0], xx, ts[rc], shift[r])
        r = (r + 1) % 4
        rc += 1
        ivc, eval_table = writeyy(file_out, prefix, yy, ivc, eval_table)
        xx = buildxx(xchoice[rc], eval_table, prefix)
        state[1] = replace_yy(ivc, eval_table, prefix)
    return ivc, eval_table, state


def md5_build_state(eval_table, prefix=""):
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

def perform_md5(eval_table, original_state, f, f3, f2=None, prefix="", rounds=64):
    state = original_state[:]
    state[0] = original_state[0][:]
    state[1] = original_state[1][:]
    state[2] = original_state[2][:]
    state[3] = original_state[3][:]
    ic = 0

    shift = [7, 12, 17, 22]
    xchoice = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0]
    if rounds <= 16:
        xchoice = xchoice[:rounds] + [0]
    ts = [0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501, 0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821]
    ic, eval_table, state = md5applyround(shift, xchoice, ts, ic, state, f, eval_table, md5round1a, prefix)

    if rounds > 16:
        shift = [5, 9, 14, 20]
        xchoice = [1, 6, 11, 0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 0]
        if rounds <= 32:
            xchoice = xchoice[:(rounds - 16)] + [0]
        ts = [0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8, 0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a]
        ic, eval_table, state = md5applyround(shift, xchoice, ts, ic, state, f, eval_table, md5round2a, prefix)

        if rounds > 32:
            shift = [4, 11, 16, 23]
            xchoice = [5, 8, 11, 14, 1, 4, 7, 10, 13, 0, 3, 6, 9, 12, 15, 2, 0]
            if rounds <= 48:
                xchoice = xchoice[:(rounds - 32)] + [0]
            ts = [0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70, 0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665]
            ic, eval_table, state = md5applyround(shift, xchoice, ts, ic, state, f, eval_table, md5round3a, prefix)

            if rounds > 48:
                shift = [6, 10, 15, 21]
                xchoice = [0, 7, 14, 5, 12, 3, 10, 1, 8, 15, 6, 13, 4, 11, 2, 9, 0]
                if rounds <= 64:
                    xchoice = xchoice[:(rounds - 48)] + [0]
                ts = [0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1, 0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391]
                ic, eval_table, state = md5applyround(shift, xchoice, ts, ic, state, f, eval_table, md5round4a, prefix)

    print(ic)
    if f != None:
        f.write("\n\n")
        f.flush()
        f.close()

    oaa = b_addl(prefix, original_state[0], state[0])
    obb = b_addl(prefix, original_state[1], state[1])
    occ = b_addl(prefix, original_state[2], state[2])
    odd = b_addl(prefix, original_state[3], state[3])

    print("MD5: " + str(rounds))
    print(b_tonum(oaa))
    print(b_tonum(obb))
    print(b_tonum(occ))
    print(b_tonum(odd))

    eval_table = writeo(f3, prefix, oaa, 'oaa', eval_table)
    eval_table = writeo(f3, prefix, obb, 'obb', eval_table)
    eval_table = writeo(f3, prefix, occ, 'occ', eval_table)
    eval_table = writeo(f3, prefix, odd, 'odd', eval_table)

    global clause_dedupe_s
    c_c = 0
    c_p = 0
    for t in clause_dedupe_s:
        if len(prefix) > 0:
            if prefix == t[0:len(prefix)]:
                eval_table[t] = clause_dedupe_s[t]
                c_p += 1
        else:
            eval_table[t] = clause_dedupe_s[t]
            c_c += 1

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

def MD5BuildBlockEvalTable(block):
    eval_table = {}
    for i in range(0, 32):
        eval_table['s' + str(i)] = b_tobitl(0x67452301)[i % 32]
    for i in range(32, 64):
        eval_table['s' + str(i)] = b_tobitl(0xefcdab89)[i % 32]
    for i in range(64, 96):
        eval_table['s' + str(i)] = b_tobitl(0x98badcfe)[i % 32]
    for i in range(96, 128):
        eval_table['s' + str(i)] = b_tobitl(0x10325476)[i % 32]
    for i in range(0, 512):
        eval_table['b' + str(i)] = b_tobitl(block[i//32])[i % 32]

    return eval_table

def MD5BuildBlockStateEvalTable(block, state):
    eval_table = {}
    for i in range(0, 32):
        if type(state[0]) == int:
            eval_table['s' + str(i)] = b_tobitl(state[0])[i % 32]
        else:
            eval_table['s' + str(i)] = state[0][i % 32]
    for i in range(32, 64):
        if type(state[1]) == int:
            eval_table['s' + str(i)] = b_tobitl(state[1])[i % 32]
        else:
            eval_table['s' + str(i)] = state[1][i % 32]
    for i in range(64, 96):
        if type(state[2]) == int:
            eval_table['s' + str(i)] = b_tobitl(state[2])[i % 32]
        else:
            eval_table['s' + str(i)] = state[2][i % 32]
    for i in range(96, 128):
        if type(state[3]) == int:
            eval_table['s' + str(i)] = b_tobitl(state[3])[i % 32]
        else:
            eval_table['s' + str(i)] = state[3][i % 32]
    for i in range(0, 512):
        if type(block[i//32]) == int:
            eval_table['b' + str(i)] = b_tobitl(block[i//32])[i % 32]
        else:
            eval_table['b' + str(i)] = block[i//32][i % 32]

    return eval_table

def compute_md5(block, in_state=None, rounds=64):
    eval_table = MD5BuildBlockEvalTable(block)

    if in_state != None:
        eval_table = MD5BuildBlockStateEvalTable(block, in_state)

    state = md5_build_state(eval_table)

    return perform_md5(eval_table, state, None, None, None, rounds=rounds)
