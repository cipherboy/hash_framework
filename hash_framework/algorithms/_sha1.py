from hash_framework.boolean import *

def sha1f(t, b, c, d):
    if 0 <= t <= 19:
        return hash_or(hash_and(b, c), hash_and(hash_not(b), d))
    elif 20 <= t <= 39:
        return simplify(('xor', b, c, d))
    elif 40 <= t <= 59:
        return simplify(('or', hash_and(b, c), hash_and(b, d), hash_and(c, d)))
    elif 60 <= t <= 79:
        return simplify(('xor', b, c, d))
    return 1//0

def sha1k(t):
    if 0 <= t <= 19:
        return hash_tobitl(0x5A827999)
    elif 20 <= t <= 39:
        return hash_tobitl(0x6ED9EBA1)
    elif 40 <= t <= 59:
        return hash_tobitl(0x8F1BBCDC)
    elif 60 <= t <= 79:
        return hash_tobitl(0xCA62C1D6)
    return 1//0

def sha1apply(func, t, b, c, d):
    result = []

    assert(len(b) == len(c))
    assert(len(c) == len(d))
    assert(len(b) == len(d))

    for i in range(0, len(b)):
        result.append(func(t, b[i], c[i], d[i]))

    return result

def sha1f32(t, b, c, d):
    return sha1apply(sha1f, t, b, c, d)

def sha1round(et, t, a, b, c, d, e, w, p):
    r, et = hash_add4l(et, p, hash_rotl(a, 5), sha1f32(t, b, c, d), e, w)
    tmp = hash_addl(r.copy(), sha1k(t).copy())
    n_a = tmp[:].copy()
    n_b = a[:].copy()
    n_c = hash_rotl(b.copy(), 30)
    n_d = c[:].copy()
    n_e = d[:].copy()
    return [n_a, n_b, n_c, n_d, n_e], et

def sha1applyrounds(ivc, state, w, file_out, eval_table, prefix=""):
    for t in range(0, 80):
        new_state, eval_table = sha1round(eval_table, t, state[0], state[1], state[2], state[3], state[4], w[t], prefix)
        for i in range(0, 5):
            ivc, eval_table = writeyy(file_out, prefix, new_state[i], ivc, eval_table)
            state[i] = replace_yy(ivc, eval_table, prefix)
        #return 1//0
    return ivc, eval_table, state

def sha1_compute_w(eval_table, f1=None, prefix=""):
    start = 0
    w = []
    for i in range(0, 16):
        t_min = i*32
        t_max = (i+1)*32
        t_w = []
        for t in range(t_min, t_max):
            s_name = prefix + "b" + str(t)
            d_name = prefix + "w" + str(t)
            if s_name in eval_table:
                s_name = eval_table[s_name]
            eval_table = write_literal(f1, d_name, s_name, eval_table, prefix)
            if d_name in eval_table:
                d_name = eval_table[d_name]

            t_w.append(d_name)
        w.append(t_w)


    for i in range(16, 80):
        t_min = i*32
        t_max = (i+1)*32
        t_3min = (i - 3)*32
        t_3max = (i - 2)*32
        t_8min = (i - 8)*32
        t_8max = (i - 7)*32
        t_14min = (i - 14)*32
        t_14max = (i - 13)*32
        t_16min = (i - 16)*32
        t_16max = (i - 15)*32

        cur_t = 0

        t_3w = []
        t_8w = []
        t_14w = []
        t_16w = []
        t_w = []

        for t in range(t_3min, t_3max):
            s_name = prefix + "w" + str(t)
            if s_name in eval_table:
                s_name = eval_table[s_name]
            t_3w.append(s_name)

        for t in range(t_8min, t_8max):
            s_name = prefix + "w" + str(t)
            if s_name in eval_table:
                s_name = eval_table[s_name]
            t_8w.append(s_name)

        for t in range(t_14min, t_14max):
            s_name = prefix + "w" + str(t)
            if s_name in eval_table:
                s_name = eval_table[s_name]
            t_14w.append(s_name)

        for t in range(t_16min, t_16max):
            s_name = prefix + "w" + str(t)
            if s_name in eval_table:
                s_name = eval_table[s_name]
            t_16w.append(s_name)

        for t in range(0, 32):
            t_w.append(simplify(('xor', t_3w[t], t_8w[t], t_14w[t], t_16w[t])))

        t_w = hash_rotl(t_w, 1)


        for t in range(t_min, t_max):
            d_name = prefix + "w" + str(t)
            eval_table = write_literal(f1, d_name, t_w[cur_t], eval_table, prefix)
            if d_name in eval_table:
                d_name = eval_table[d_name]
            t_w[cur_t] = d_name
            cur_t += 1
        w.append(t_w)

    return w, eval_table

def sha1_build_state(eval_table, prefix=""):
    state = [[], [], [], [], []]
    for i in range(0, 160):
        name = prefix + "s" + str(i)
        l = i//32
        if name in eval_table:
            state[l].append(eval_table[name])
        else:
            state[l].append(name)
    return state

def perform_sha1(eval_table, original_state, f=None, f1=None, f2=None, f3=None, prefix=""):
    state = original_state[:]
    state[0] = original_state[0][:]
    state[1] = original_state[1][:]
    state[2] = original_state[2][:]
    state[3] = original_state[3][:]
    state[4] = original_state[4][:]
    ic = 0

    print("Computing extensions...")
    w, eval_table = sha1_compute_w(eval_table, f1, prefix)

    print("Computing rounds...")
    ic, eval_table, state = sha1applyrounds(ic, state, w, f, eval_table, prefix)

    print(ic)
    if f != None:
        f.write("\n\n")
        f.flush()
        f.close()

    oaa = hash_addl(original_state[0], state[0])
    obb = hash_addl(original_state[1], state[1])
    occ = hash_addl(original_state[2], state[2])
    odd = hash_addl(original_state[3], state[3])
    oee = hash_addl(original_state[4], state[4])

    print(hash_tonum(oaa))
    print(hash_tonum(obb))
    print(hash_tonum(occ))
    print(hash_tonum(odd))
    print(hash_tonum(oee))

    eval_table = writeo(f3, prefix, oaa, 'oaa', eval_table)
    eval_table = writeo(f3, prefix, obb, 'obb', eval_table)
    eval_table = writeo(f3, prefix, occ, 'occ', eval_table)
    eval_table = writeo(f3, prefix, odd, 'odd', eval_table)
    eval_table = writeo(f3, prefix, oee, 'oee', eval_table)
    stats = []

    print("Generating stats...")
    for i in eval_table:
        stats.append(var_count(eval_table[i]))
    print(list(map(lambda x: (x, stats.count(x)), set(stats))))

    global clause_dedupe_s
    print("Deduplicated clauses: " + str(len(clause_dedupe_s)))
    print("Clauses:")

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

    print(str(c_c) + " " + str(c_p))
    print("--")

    if f2 != None:
        for t in clause_dedupe_s:
            if len(prefix) > 0:
                if prefix == t[0:len(prefix)]:
                    if t != translate(clause_dedupe_s[t]):
                        f2.write(t + " := " + translate(clause_dedupe_s[t]) + ";\n")
            else:
                if t != translate(clause_dedupe_s[t]):
                    f2.write(t + " := " + translate(clause_dedupe_s[t]) + ";\n")


    if f3 != None:
        f3.write("\n\n")
        f3.flush()
        f3.close()

    if f1 != None:
        f1.write("\n\n")
        f1.flush()
        f1.close()

    return eval_table

def compute_sha1(block, state=None):
    eval_table = SHA1BuildBlockEvalTable(block)

    if state == None:
        state = sha1_build_state(eval_table)
    else:
        eval_table = SHA1BuildBlockStateEvalTable(block, state)
        state = sha1_build_state(eval_table)

    return perform_sha1(eval_table, state, None, None, None, None, "")
