from hash_framework.boolean import *

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


def build_sipmodel():
    block_len = 1
    block_rounds = 1
    post_rounds = 1
    hashlen128 = False
    collision = True

    giv = 0
    get = {}

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
