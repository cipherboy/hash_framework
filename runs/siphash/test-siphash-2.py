import sys, collections
import hash_framework as hf


def get_mapping(cnf="problem.cnf"):
    var_mapping = collections.defaultdict(list)

    f_cnf = open(cnf, "r")

    for l in f_cnf:
        if len(l) > 0 and l[0] == "c" and " <-> " in l:
            l_var = l[1:].split(" <-> ")
            l_var[0] = l_var[0].strip()
            l_var[1] = l_var[1].strip()
            var_mapping[l_var[1]].append(l_var[0])

    return dict(var_mapping)


def callback(result):
    r = result
    h1s0 = get_var64s(r, "gk1b")
    h1s1 = get_var64s(r, "gk2b")
    h1s0 = bit64_to_hex(h1s0)
    h1s1 = bit64_to_hex(h1s1)
    print((h1s0, h1s1))


def load_results(out="problem.out", cnf="problem.cnf"):
    f_out = open(out, "r")
    var_mapping = get_mapping(cnf=cnf)
    result = None
    for l in f_out:
        if l[0] == "s":
            if result != None:
                callback(result)
            result = {}
        if l[0] == "v":
            end = -2
            if l[end] == "0":
                end = -3
            l_assigns = l[2:end].split(" ")
            for v in l_assigns:
                if len(v) == 0:
                    print(out)
                    print(cnf)
                    continue
                var = v
                val = "T"
                if v[0] == "-":
                    var = v[1:]
                    val = "F"
                if var in var_mapping:
                    for loc in var_mapping[var]:
                        result[loc] = val
    if result != None and result != {}:
        callback(result)


def get_var64(r, prefix):
    result = []
    for i in range(0, 64):
        result.append(r[prefix + str(i)])
    return result


def get_var64s(r, prefix):
    result = []
    for i in range(0, 64):
        result.append(r[prefix + str(i)])
    return "".join(result)


def bit64_to_hex(num):
    t1 = num[0:32]
    t2 = num[32:]
    return hf.boolean.b_block_to_hex_reverse(
        [hf.boolean.b_tonum(t1), hf.boolean.b_tonum(t2)]
    )


def hex_to_bit64(hex):
    t = list(map(hf.boolean.b_tobitl, hf.boolean.b_reverse_hex_to_block(hex)))
    return t[0] + t[1]


def run():
    import hash_framework.algorithms._siphash as _sh
    import hash_framework as hf

    key_unknown_bits = 16
    number_of_blocks = 4
    block_len = 1
    block_rounds = 1
    final_rounds = 0

    for fr in [0, 1, 2, 3]:
        for br in [1, 2]:
            for nb in range(1, 17):
                for kub in range(0, 65, 2):
                    print((kub, nb, br, fr))
                    mdir = (
                        "kub"
                        + str(kub)
                        + "-nb"
                        + str(nb)
                        + "-br"
                        + str(br)
                        + "-fr"
                        + str(fr)
                    )
                    m = hf.models()
                    m.start(mdir, False)
                    base_dir = m.model_dir + "/" + mdir
                    _sh.build_test_key_leakage(
                        dir=base_dir,
                        key_unknown_bits=kub,
                        number_of_blocks=nb,
                        block_rounds=br,
                        final_rounds=fr,
                    )
                    m.collapse()
                    m.build()
                    m.remote = False
                    m.run(count=2)
                    load_results(base_dir + "/problem.out", base_dir + "/problem.cnf")


run()
