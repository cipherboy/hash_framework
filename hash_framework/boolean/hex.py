from hash_framework.boolean.core import *

def b_hex_to_block(blk):
    assert(len(blk) % 8 == 0)
    b = []
    for i in range(0, len(blk)//8):
        a = blk[8*i:8*(i+1)]
        w = int(a[0:2], 16)
        x = int(a[2:4], 16)
        y = int(a[4:6], 16)
        z = int(a[6:8], 16)
        b.append(w + x*256 + y*256*256 + z*256*256*256)
    return b

def b_reverse_hex_to_block(blk):
    assert(len(blk) % 8 == 0)
    b = []
    for i in range(0, len(blk)//8):
        a = blk[8*i:8*(i+1)]
        w = int(a[0:2], 16)
        x = int(a[2:4], 16)
        y = int(a[4:6], 16)
        z = int(a[6:8], 16)
        b.append(z + y*256 + x*256*256 + w*256*256*256)
    return b

def b_block_to_hex(block):
    r = ""
    for i in block:
        r+=(hex(b_tonum_correct(b_tobitl(i)))[2:]).zfill(8)
    return r


def b_block_to_hex_reverse(block):
    r = ""
    for i in block:
        r+=(hex(b_tonum(b_tobitl(i)))[2:]).zfill(8)
    return r
