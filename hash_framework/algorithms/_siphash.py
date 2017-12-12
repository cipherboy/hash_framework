from hash_framework.boolean import *
import random

def sipround(v0, v1, v2, v3, iv, et):
    nv0 = v0.copy()
    nv1 = v1.copy()
    nv2 = v2.copy()
    nv3 = v3.copy()

    nv0 = b_addl(nv0, nv1)
    nv0, iv, et = update_et(nv0, iv, et)
    nv1 = b_rotl(nv1, 13)
    nv1, iv, et = update_et(nv1, iv, et)
    nv1 = b_xorw(nv1, nv0)
    nv1, iv, et = update_et(nv1, iv, et)
    nv0 = b_rotl(nv0, 32)
    nv0, iv, et = update_et(nv0, iv, et)
    nv2 = b_addl(nv2, nv3)
    nv2, iv, et = update_et(nv2, iv, et)
    nv3 = b_rotl(nv3, 16)
    nv3, iv, et = update_et(nv3, iv, et)
    nv3 = b_xorw(nv3, nv2)
    nv3, iv, et = update_et(nv3, iv, et)
    nv0 = b_addl(nv0, nv3)
    nv0, iv, et = update_et(nv0, iv, et)
    nv3 = b_rotl(nv3, 21)
    nv3, iv, et = update_et(nv3, iv, et)
    nv3 = b_xorw(nv3, nv0)
    nv3, iv, et = update_et(nv3, iv, et)
    nv2 = b_addl(nv2, nv1)
    nv2, iv, et = update_et(nv2, iv, et)
    nv1 = b_rotl(nv1, 17)
    nv1, iv, et = update_et(nv1, iv, et)
    nv1 = b_xorw(nv1, nv2)
    nv1, iv, et = update_et(nv1, iv, et)
    nv2 = b_rotl(nv2, 32)
    nv2, iv, et = update_et(nv2, iv, et)

    return (nv0, nv1, nv2, nv3), iv, et

def rsipround(v0, v1, v2, v3):
    nv0 = v0.copy()
    nv1 = v1.copy()
    nv2 = v2.copy()
    nv3 = v3.copy()

    nv0 = b_addl(nv0, nv1)
    nv1 = b_rotl(nv1, 13)
    nv1 = b_xorw(nv1, nv0)
    nv0 = b_rotl(nv0, 32)
    nv2 = b_addl(nv2, nv3)
    nv3 = b_rotl(nv3, 16)
    nv3 = b_xorw(nv3, nv2)
    nv0 = b_addl(nv0, nv3)
    nv3 = b_rotl(nv3, 21)
    nv3 = b_xorw(nv3, nv0)
    nv2 = b_addl(nv2, nv1)
    nv1 = b_rotl(nv1, 17)
    nv1 = b_xorw(nv1, nv2)
    nv2 = b_rotl(nv2, 32)

    return (nv0, nv1, nv2, nv3)


def compute_siphash(k1, k2, blocks, block_rounds=1, final_rounds=3):
    giv = 0
    get = {}

    iv0 = hex_to_bit64("736f6d6570736575")
    iv1 = hex_to_bit64("646f72616e646f6d")
    iv2 = hex_to_bit64("6c7967656e657261")
    iv3 = hex_to_bit64("7465646279746573")

    s = (iv0, iv1, iv2, iv3)
    s = list(s)
    s[0] = b_xorw(s[0], k1)
    s[1] = b_xorw(s[1], k2)
    s[2] = b_xorw(s[2], k1)
    s[3] = b_xorw(s[3], k2)
    s = tuple(s)

    for i in range(0, len(blocks)):
        mb = blocks[i]

        s = list(s)
        s[3] = b_xorw(s[3], mb)
        s = tuple(s)

        for j in range(0, block_rounds):
            ns = rsipround(s[0], s[1], s[2], s[3])
            s = ns

        s = list(s)
        s[0] = b_xorw(s[0], mb)
        s = tuple(s)

    for j in range(0, final_rounds):
        ns = rsipround(s[0], s[1], s[2], s[3])
        s = ns

    return s


def update_et(var, iv, et):
    nv = []
    for i in range(0, len(var)):
        name = "t" + str(iv)
        et[name] = var[i]
        nv.append(name)
        iv += 1
    return nv, iv, et

def hex_to_bit64(hex):
    t = list(map(b_tobitl, b_reverse_hex_to_block(hex)))
    return t[0] + t[1]

def bit64_to_hex(num):
    t1 = num[0:32]
    t2 = num[32:]
    return b_block_to_hex_reverse([b_tonum(t1), b_tonum(t2)])

def print_state(v0, v1, v2, v3):
    return
    print("v0: " + bit64_to_hex(v0))
    print("v1: " + bit64_to_hex(v1))
    print("v2: " + bit64_to_hex(v2))
    print("v3: " + bit64_to_hex(v3))
    print("")

def test_sipround():
    build_sipmodel

def write_state(prefix, s, name):
    f = open(name, 'w')
    for e in range(0, 4):
        for i in range(0, 64):
            name = prefix + str(e) + "b" + str(i)
            if type(s[e][i]) == tuple:
                f.write(name + " := " + translate(s[e][i]) + ";\n")
            elif type(s[e][i]) == str:
                f.write(name + " := " + s[e][i] + ";\n")
            s[e][i] = name
    f.flush()
    f.close()
    return s

def write_et(et, name):
    f = open(name, 'w')
    for k in et:
        f.write(k + " := " + translate(et[k]) + ";\n")
    f.flush()
    f.close()

def build_state(prefix):
    s = []
    for i in range(0, 4):
        sa = []
        for j in range(0, 64):
            sa.append(prefix + str(i) + "i" + str(j))
        s.append(sa)
    return s

def write_key(k1, k2, k1prefix, k2prefix, fname="01-key.txt", bits=64):
    f = open(fname, 'w')
    for i in range(0, bits):
        f.write(k1prefix + str(i) + " := " + k1[i] + ";\n")
    for i in range(0, bits):
        f.write(k2prefix + str(i) + " := " + k2[i] + ";\n")
    f.flush()
    f.close()

def write_block(blk, prefix, fname="05-block.txt", bits=64):
    f = open(fname, 'w')
    for i in range(0, bits):
        f.write(prefix + str(i) + " := " + blk[i] + ";\n")

    f.flush()
    f.close()

def write_output_state(os, prefix, middle, name, fname="06-output.txt", bits=64):
    cstate = ['and']
    for i in range(0, 4):
        for j in range(0, bits):
            cstate.append(('equal', prefix + str(i) + middle + str(j), os[i][j]))
    f = open(fname, 'w')
    f.write(name + ' := ' + translate(tuple(cstate)) + ";\n")
    f.flush()
    f.close()


def write_output(os, prefix, name, fname="06-output.txt", bits=64):
    coutput = ['and']
    for j in range(0, bits):
        coutput.append(('equal', prefix + str(j), os[j]))
    f = open(fname, 'w')
    f.write(name + ' := ' + translate(tuple(coutput)) + ";\n")
    f.flush()
    f.close()

def gen_random_state(prefix):
    output = ['and']
    for i in range(0, 4):
        for j in range(0, 64):
            if random.randint(0, 1) == 0:
                output.append(prefix + str(i) + "b" + str(j))
            else:
                output.append(('not', "h1iv" + str(i) + "b" + str(j)))
    f = open("97-output.txt", 'w')
    f.write('coutput := ' + translate(tuple(output)) + ";\n")
    f.flush()
    f.close()

def gen_random_key():
    k1 = []
    k2 = []
    for i in range(0, 64):
        if random.randint(0, 1) == 0:
            k1.append('T')
        else:
            k1.append('F')

        if random.randint(0, 1) == 0:
            k2.append('T')
        else:
            k2.append('F')

    return k1, k2

def gen_random_block():
    blk = []
    for i in range(0, 64):
        if random.randint(0, 1) == 0:
            blk.append('T')
        else:
            blk.append('F')
    return blk

def build_test_key_leakage():
    key_unknown_bits = 64
    number_of_blocks = 512
    block_len = 1
    block_rounds = 1
    final_rounds = 3

    giv = 0
    get = {}

    gk1, gk2 = gen_random_key()
    k1 = []
    for k in range(0, 64):
        k1.append("gk1b" + str(k))
    k2 = []
    for k in range(0, 64):
        k2.append("gk2b" + str(k))
    write_key(gk1, gk2, "gk1b", "gk2b", bits=(64 - key_unknown_bits))
    print((bit64_to_hex(gk1), bit64_to_hex(gk2)))
    write_key(gk1, gk2, "gk1b", "gk2b", fname="actual.key")

    cout = ['and']

    for i in range(0, number_of_blocks):
        prefix = "h" + str(i)
        gmb = gen_random_block()
        go = compute_siphash(gk1, gk2, [gmb], block_rounds=block_rounds, final_rounds=final_rounds)
        gos = b_xorw(b_xorw(go[0],go[1]), b_xorw(go[2],go[3]))

        iv0 = hex_to_bit64("736f6d6570736575")
        iv1 = hex_to_bit64("646f72616e646f6d")
        iv2 = hex_to_bit64("6c7967656e657261")
        iv3 = hex_to_bit64("7465646279746573")

        s = (iv0, iv1, iv2, iv3)
        s = list(s)
        s[0] = b_xorw(s[0], k1)
        s[1] = b_xorw(s[1], k2)
        s[2] = b_xorw(s[2], k1)
        s[3] = b_xorw(s[3], k2)
        s = tuple(s)
        name = prefix + "iv"
        fname = "01-" + prefix + "-initial.txt"
        s = write_state(name, s, fname)

        for i in range(0, block_len):
            mb = []
            for k in range(0, 64):
                mb.append(prefix + "m" + str(i) + "b" + str(k))
            write_block(gmb, prefix + "m" + str(i) + "b", fname="05-" + prefix + "-block.txt")

            s = list(s)
            s[3] = b_xorw(s[3], mb)
            s = tuple(s)

            for j in range(0, block_rounds):
                ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
                name = prefix + "b" + str(i) + "r" + str(j) + "v"
                fname = "02-" + prefix + "-b" + str(i) + "-r" + str(j) + "-sipround.txt"
                s = write_state(name, ns, fname)

            s = list(s)
            s[0] = b_xorw(s[0], mb)
            s = tuple(s)


        for j in range(0, final_rounds):
            ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
            name = prefix + "r" + str(j) + "v"
            fname = "03-" + prefix + "-r" + str(j) + "-sipround.txt"
            s = write_state(name, ns, fname)

        name = prefix + "o"
        fname = "03-" + prefix + "-output.txt"
        s = write_state(name, s, fname)


        os = b_xorw(b_xorw(s[0],s[1]),b_xorw(s[2],s[3]))
        name = prefix + "os"
        fname = "04-" + prefix + "-output.txt"
        f = open(fname, 'w')
        for i in range(0, 64):
            name = prefix + "os" + str(i)
            f.write(name + " := " + translate(os[i]) + ";\n")
        f.flush()
        f.close()

        # write_output_state(go, prefix + "o", "b", prefix + "os", fname="06-" + prefix + "-block.txt")
        write_output(gos, prefix + "os", "f" + prefix+"os", fname="06-" + prefix + "-block.txt")
        cout.append("f" + prefix + "os")

    f = open("00-header.txt", 'w')
    f.write("BC1.1\n\n")
    f.flush()
    f.close()

    write_et(get, "50-all-flat.txt")

    f = open("98-out.txt", 'w')
    f.write('cout := ' + translate(tuple(cout)) + ";\n")
    f.flush()
    f.close()

    f = open("99-problem.txt", 'w')
    f.write("ASSIGN cout;\n\n")
    f.flush()
    f.close()

def build_test_block_output_key():
    block_len = 2
    block_rounds = 2

    giv = 0
    get = {}

    for prefix in ['h']:
        iv0 = hex_to_bit64("736f6d6570736575")
        iv1 = hex_to_bit64("646f72616e646f6d")
        iv2 = hex_to_bit64("6c7967656e657261")
        iv3 = hex_to_bit64("7465646279746573")

        k1 = []
        for k in range(0, 64):
            k1.append(prefix + "ok1" + "b" + str(k))
        k2 = []
        for k in range(0, 64):
            k2.append(prefix + "ok2" + "b" + str(k))

        s = (iv0, iv1, iv2, iv3)
        s = list(s)
        s[0] = b_xorw(s[0], k1)
        s[1] = b_xorw(s[1], k2)
        s[2] = b_xorw(s[2], k1)
        s[3] = b_xorw(s[3], k2)
        s = tuple(s)
        name = prefix + "oiv"
        fname = "01-" + prefix + "-other.txt"
        s = write_state(name, s, fname)

        k1 = []
        for k in range(0, 64):
            k1.append(prefix + "k1" + "b" + str(k))
        k2 = []
        for k in range(0, 64):
            k2.append(prefix + "k2" + "b" + str(k))

        s = (iv0, iv1, iv2, iv3)
        s = list(s)
        s[0] = b_xorw(s[0], k1)
        s[1] = b_xorw(s[1], k2)
        s[2] = b_xorw(s[2], k1)
        s[3] = b_xorw(s[3], k2)
        s = tuple(s)
        name = prefix + "iv"
        fname = "01-" + prefix + "-initial.txt"
        s = write_state(name, s, fname)

        for i in range(0, block_len):
            mb = []
            for k in range(0, 64):
                mb.append(prefix + "m" + str(i) + "b" + str(k))

            s = list(s)
            s[3] = b_xorw(s[3], mb)
            s = tuple(s)

            for j in range(0, block_rounds):
                ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
                name = prefix + "b" + str(i) + "r" + str(j) + "v"
                fname = "02-" + prefix + "-b" + str(i) + "-r" + str(j) + "-sipround.txt"
                s = write_state(name, ns, fname)

            s = list(s)
            s[0] = b_xorw(s[0], mb)
            s = tuple(s)

        name = prefix + "o"
        fname = "03-" + prefix + "-output.txt"
        s = write_state(name, s, fname)

    f = open("00-header.txt", 'w')
    f.write("BC1.1\n\n")
    f.flush()
    f.close()


    cfixed = ['and']
    for i in range(0, 4):
        for j in range(0, 64):
            cfixed.append(('equal', 'hoiv' + str(i) + "b" + str(j), 'ho' + str(i) + "b" + str(j)))
    f = open("98-fixed.txt", 'w')
    f.write('cfixed := ' + translate(tuple(cfixed)) + ";\n")
    f.flush()
    f.close()

    write_et(get, "50-all-flat.txt")

    f = open("99-problem.txt", 'w')
    f.write("ASSIGN cfixed;\n\n")
    f.flush()
    f.close()


def build_test_block_fixed():
    block_len = 1
    block_rounds = 2

    giv = 0
    get = {}

    for prefix in ['h']:
        iv0 = hex_to_bit64("736f6d6570736575")
        iv1 = hex_to_bit64("646f72616e646f6d")
        iv2 = hex_to_bit64("6c7967656e657261")
        iv3 = hex_to_bit64("7465646279746573")

        k1 = []
        for k in range(0, 64):
            k1.append(prefix + "k1" + "b" + str(k))

        k2 = []
        for k in range(0, 64):
            k2.append(prefix + "k2" + "b" + str(k))

        s = (iv0, iv1, iv2, iv3)
        s = list(s)
        s[0] = b_xorw(s[0], k1)
        s[1] = b_xorw(s[1], k2)
        s[2] = b_xorw(s[2], k1)
        s[3] = b_xorw(s[3], k2)
        s = tuple(s)
        name = prefix + "iv"
        fname = "01-" + prefix + "-initial.txt"
        s = write_state(name, s, fname)

        for i in range(0, block_len):
            mb = []
            for k in range(0, 64):
                mb.append(prefix + "m" + str(i) + "b" + str(k))

            s = list(s)
            s[3] = b_xorw(s[3], mb)
            s = tuple(s)

            for j in range(0, block_rounds):
                ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
                name = prefix + "b" + str(i) + "r" + str(j) + "v"
                fname = "02-" + prefix + "-b" + str(i) + "-r" + str(j) + "-sipround.txt"
                s = write_state(name, ns, fname)

            s = list(s)
            s[0] = b_xorw(s[0], mb)
            s = tuple(s)

        name = prefix + "o"
        fname = "03-" + prefix + "-output.txt"
        s = write_state(name, s, fname)

    f = open("00-header.txt", 'w')
    f.write("BC1.1\n\n")
    f.flush()
    f.close()


    cfixed = ['and']
    for i in range(0, 4):
        for j in range(0, 64):
            cfixed.append(('equal', 'hiv' + str(i) + "b" + str(j), 'ho' + str(i) + "b" + str(j)))
    f = open("98-fixed.txt", 'w')
    f.write('cfixed := ' + translate(tuple(cfixed)) + ";\n")
    f.flush()
    f.close()

    write_et(get, "50-all-flat.txt")

    f = open("99-problem.txt", 'w')
    f.write("ASSIGN cfixed;\n\n")
    f.flush()
    f.close()


def build_test_block_invert():
    block_len = 1
    block_rounds = 1

    giv = 0
    get = {}

    for prefix in ['h']:
        iv0 = hex_to_bit64("736f6d6570736575")
        iv1 = hex_to_bit64("646f72616e646f6d")
        iv2 = hex_to_bit64("6c7967656e657261")
        iv3 = hex_to_bit64("7465646279746573")

        k1 = []
        for k in range(0, 64):
            k1.append(prefix + "k1" + "b" + str(k))

        k2 = []
        for k in range(0, 64):
            k2.append(prefix + "k2" + "b" + str(k))

        s = (iv0, iv1, iv2, iv3)
        s = list(s)
        s[0] = b_xorw(s[0], k1)
        s[1] = b_xorw(s[1], k2)
        s[2] = b_xorw(s[2], k1)
        s[3] = b_xorw(s[3], k2)
        s = tuple(s)
        name = prefix + "iv"
        fname = "01-" + prefix + "-initial.txt"
        s = write_state(name, s, fname)

        for i in range(0, block_len):
            mb = []
            for k in range(0, 64):
                mb.append(prefix + "m" + str(i) + "b" + str(k))

            s = list(s)
            s[3] = b_xorw(s[3], mb)
            s = tuple(s)

            for j in range(0, block_rounds):
                ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
                name = prefix + "b" + str(i) + "r" + str(j) + "v"
                fname = "02-" + prefix + "-b" + str(i) + "-r" + str(j) + "-sipround.txt"
                s = write_state(name, ns, fname)

            s = list(s)
            s[0] = b_xorw(s[0], mb)
            s = tuple(s)

        name = prefix + "o"
        fname = "03-" + prefix + "-output.txt"
        s = write_state(name, s, fname)

    f = open("00-header.txt", 'w')
    f.write("BC1.1\n\n")
    f.flush()
    f.close()


    output = ['and']
    for i in range(0, 4):
        for j in range(0, 64):
            output.append(('equal', 'ho' + str(i) + "b" + str(j), "F"))

    f = open("97-output.txt", 'w')
    f.write('coutput := ' + translate(tuple(output)) + ";\n")
    f.flush()
    f.close()

    write_et(get, "50-all-flat.txt")

    f = open("99-problem.txt", 'w')
    f.write("ASSIGN coutput;\n\n")
    f.flush()
    f.close()


def build_test_strong_block_collision():
    block_len = 2
    block_rounds = 1

    giv = 0
    get = {}

    for prefix in ['h1', 'h2']:
        s = build_state(prefix + "in")

        for i in range(0, block_len):
            mb = []
            for k in range(0, 64):
                mb.append(prefix + "m" + str(i) + "b" + str(k))

            s = list(s)
            s[3] = b_xorw(s[3], mb)
            s = tuple(s)

            for j in range(0, block_rounds):
                ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
                name = prefix + "b" + str(i) + "r" + str(j) + "v"
                fname = "02-" + prefix + "-b" + str(i) + "-r" + str(j) + "-sipround.txt"
                s = write_state(name, ns, fname)

            s = list(s)
            s[0] = b_xorw(s[0], mb)
            s = tuple(s)

        name = prefix + "o"
        fname = "03-" + prefix + "-output.txt"
        s = write_state(name, s, fname)

    f = open("00-header.txt", 'w')
    f.write("BC1.1\n\n")
    f.flush()
    f.close()

    collision = ['and']
    for i in range(0, 4):
        for j in range(0, 64):
            collision.append(('equal', 'h1o' + str(i) + "b" + str(j), "h2o" + str(i) + "b" + str(j)))
    f = open("98-collision.txt", 'w')
    f.write('ccollision := ' + translate(tuple(collision)) + ";\n")
    f.flush()
    f.close()

    cblock = ['and']
    for i in range(0, block_len):
        for k in range(0, 64):
            cblock.append(('equal', 'h1m' + str(i) + 'b' + str(k), "h2m" + str(i) + "b" + str(k)))
    f = open("96-block.txt", 'w')
    f.write('cblock := ' + translate(('not', tuple(cblock))) + ";\n")
    f.flush()
    f.close()

    cinput = ['and']
    for i in range(0, 4):
        for j in range(0, 64):
            cinput.append(('equal', 'h1in' + str(i) + "i" + str(j), "h2in" + str(i) + "i" + str(j)))
    f = open("97-input.txt", 'w')
    f.write('cinput := ' + translate(tuple(cinput)) + ";\n")
    f.flush()
    f.close()

    write_et(get, "50-all-flat.txt")

    f = open("99-problem.txt", 'w')
    f.write("ASSIGN ccollision, cinput, cblock;\n\n")
    f.flush()
    f.close()


def build_test_fixed():
    rounds = 3

    giv = 0
    get = {}
    for prefix in ["h"]:
        s = build_state("hin")

        for r in range(0, rounds):
            ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
            name = "r" + str(r) + "s"
            fname = "02-" + name + "-siphash.txt"
            s = write_state(name, ns, fname)

        name = prefix + "o"
        fname = "03-" + prefix + "-output.txt"
        s = write_state(name, s, fname)

    f = open("00-header.txt", 'w')
    f.write("BC1.1\n\n")
    f.flush()
    f.close()

    cinput = ['or']
    for i in range(0, 4):
        for j in range(0, 64):
            cinput.append('hin' + str(i) + "i" + str(j))
    f = open("96-input.txt", 'w')
    f.write('cinput := ' + translate(tuple(cinput)) + ";\n")
    f.flush()
    f.close()

    cintermediate = ['and']
    for i in range(0, 4):
        for j in range(0, 64):
            cintermediate.append(('equal', 'hin' + str(i) + "i" + str(j), 'h1r0s' + str(i) + "b" + str(j)))
    f = open("97-intermediate.txt", 'w')
    f.write('cintermediate := ' + translate(('not', tuple(cintermediate))) + ";\n")
    f.flush()
    f.close()

    cfixed = ['and']
    for i in range(0, 4):
        for j in range(0, 64):
            cfixed.append(('equal', 'hin' + str(i) + "i" + str(j), 'ho' + str(i) + "b" + str(j)))
    f = open("98-fixed.txt", 'w')
    f.write('cfixed := ' + translate(tuple(cfixed)) + ";\n")
    f.flush()
    f.close()

    write_et(get, "50-all-flat.txt")

    f = open("99-problem.txt", 'w')
    f.write("ASSIGN cfixed, cinput, cintermediate;\n\n")
    f.flush()
    f.close()



def build_test_invert(rounds=3):
    giv = 0
    get = {}
    for prefix in ["h1"]:
        s = build_state("in")

        for r in range(0, rounds):
            ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
            name = "r" + str(r) + "s"
            fname = "02-" + name + "-siphash.txt"
            s = write_state(name, ns, fname)

    gen_random_state("r" + str(r) + "s")

    f = open("00-header.txt", 'w')
    f.write("BC1.1\n\n")
    f.flush()
    f.close()

    write_et(get, "50-all-flat.txt")

    f = open("99-problem.txt", 'w')
    f.write("ASSIGN coutput;\n\n")
    f.flush()
    f.close()


def build_test_xor():
    block_len = 1
    block_rounds = 1
    post_rounds = 1
    hashlen128 = False
    collision = True

    giv = 0
    get = {}
    for prefix in ["h1", "h2"]:
        s = build_state(prefix + "in")

        ss = b_xorw(b_xorw(s[0],s[1]),b_xorw(s[2],s[3]))
        name = prefix + "ss"
        fname = "01-" + prefix + "-input.txt"
        f = open(fname, 'w')
        for i in range(0, 64):
            name = prefix + "ss" + str(i)
            f.write(name + " := " + translate(ss[i]) + ";\n")
        f.flush()
        f.close()


        ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
        name = prefix + "iv"
        fname = "02-" + prefix + "-siphash.txt"
        s = write_state(name, ns, fname)

        os = b_xorw(b_xorw(s[0],s[1]),b_xorw(s[2],s[3]))
        name = prefix + "os"
        fname = "03-" + prefix + "-output.txt"
        f = open(fname, 'w')
        for i in range(0, 64):
            name = prefix + "os" + str(i)
            f.write(name + " := " + translate(os[i]) + ";\n")
        f.flush()
        f.close()

    f = open("00-header.txt", 'w')
    f.write("BC1.1\n\n")
    f.flush()
    f.close()

    collision = ['and']
    for i in range(0, 64):
        name1 = "h1os" + str(i)
        name2 = "h2os" + str(i)
        collision.append(('equal', name1, name2))
    f = open("98-collision.txt", 'w')
    f.write('ccollision := ' + translate(tuple(collision)) + ";\n")
    f.flush()
    f.close()

    collision = ['and']
    for i in range(0, 64):
        name1 = "h1ss" + str(i)
        name2 = "h2ss" + str(i)
        collision.append(('equal', name1, name2))
    f = open("97-input.txt", 'w')
    f.write('cinput := ' + translate(tuple(collision)) + ";\n")
    f.flush()
    f.close()

    cblocks = ['and']
    for i in range(0, 4):
        for k in range(0, 64):
            name1 = "h1in" + str(i) + "i" + str(k)
            name2 = "h2in" + str(i) + "i" + str(k)
            cblocks.append(('equal', name1, name2))
    f = open("96-different.txt", 'w')
    f.write('cdifferent := ' + translate(('not', tuple(cblocks))) + ";\n")
    f.flush()
    f.close()

    write_et(get, "50-all-flat.txt")

    f = open("99-problem.txt", 'w')
    f.write("ASSIGN ccollision, cinput, cdifferent;\n\n")
    f.flush()
    f.close()

def build_sipmodel():
    block_len = 1
    block_rounds = 1
    post_rounds = 1
    hashlen128 = False
    collision = True

    giv = 0
    get = {}

    build_test_xor()
    return

    for prefix in ['h1', 'h2']:
        iv0 = hex_to_bit64("736f6d6570736575")
        iv1 = hex_to_bit64("646f72616e646f6d")
        iv2 = hex_to_bit64("6c7967656e657261")
        iv3 = hex_to_bit64("7465646279746573")

        s = (iv0, iv1, iv2, iv3)
        name = prefix + "iv"
        fname = "01-" + prefix + "-initial.txt"
        s = write_state(name, s, fname)

        for i in range(0, block_len):
            mb = []
            for k in range(0, 64):
                mb.append(prefix + "m" + str(i) + "b" + str(k))

            s = list(s)
            s[3] = b_xorw(s[3], mb)
            s = tuple(s)

            for j in range(0, block_rounds):
                ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
                name = prefix + "b" + str(i) + "r" + str(j) + "v"
                fname = "02-" + prefix + "-b" + str(i) + "-r" + str(j) + "-sipround.txt"
                s = write_state(name, ns, fname)

            s = list(s)
            s[0] = b_xorw(s[0], mb)
            s = tuple(s)

        for i in range(0, post_rounds):
            ns, giv, get = sipround(s[0], s[1], s[2], s[3], giv, get)
            name = prefix + "pr" + str(i) + "v"
            fname = "03-" + prefix + "-pr" + str(i) + "-sipround.txt"
            s = write_state(name, ns, fname)

        os = b_xorw(b_xorw(s[0],s[1]),b_xorw(s[2],s[3]))
        name = prefix + "os"
        fname = "04-" + prefix + "-output.txt"
        f = open(fname, 'w')
        for i in range(0, 64):
            name = prefix + "os" + str(i)
            f.write(name + " := " + translate(os[i]) + ";\n")
        f.flush()
        f.close()

    if collision:
        collision = ['and']
        for i in range(0, 64):
            name1 = "h1os" + str(i)
            name2 = "h2os" + str(i)
            collision.append(('equal', name1, name2))
        f = open("98-collision.txt", 'w')
        f.write('ccollision := ' + translate(tuple(collision)) + ";\n")
        f.flush()
        f.close()

        cblocks = ['and']
        for i in range(0, block_len):
            for k in range(0, 64):
                name1 = "h1m" + str(i) + "b" + str(k)
                name2 = "h2m" + str(i) + "b" + str(k)
                cblocks.append(('equal', name1, name2))
        f = open("97-blocks.txt", 'w')
        f.write('cblocks := ' + translate(('not', tuple(cblocks))) + ";\n")
        f.flush()
        f.close()

    write_et(get, "50-all-flat.txt")

    print("Done")
