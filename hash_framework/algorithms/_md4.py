from hash_framework.boolean import *

def md4f(x, y, z):
    return b_or(b_and(x, y), b_and(b_not(x), z))

def md4g(x, y, z):
    return b_or(b_or(b_and(x, y), b_and(x, z)), b_and(y, z))

def md4h(x, y, z):
    return b_xor(b_xor(x, y), z)

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
    return b_rotl(b_addl(b_addl(a, md4f32(b, c, d)), x), l)

def md4round2a(a, b, c, d, x, l):
    return b_rotl(b_addl(b_addl(b_addl(a, b_tobitl(0x5A827999)), md4g32(b, c, d)), x), l)

def md4round3a(a, b, c, d, x, l):
    return b_rotl(b_addl(b_addl(b_addl(a, b_tobitl(0x6ED9EBA1)), md4h32(b, c, d)), x), l)

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

    oaa = b_addl(original_state[0], state[0])
    obb = b_addl(original_state[1], state[1])
    occ = b_addl(original_state[2], state[2])
    odd = b_addl(original_state[3], state[3])

    print(b_tonum(oaa))
    print(b_tonum(obb))
    print(b_tonum(occ))
    print(b_tonum(odd))

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
