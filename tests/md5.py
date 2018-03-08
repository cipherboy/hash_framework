#!/usr/bin/env python3

import hash_framework.algorithms._md5 as h
import hash_framework as hf
from hash_framework.boolean import *

def tc_zero_block():
    in_block_bin = ['T'] + ['F']*511
    in_block = []
    for i in range(0, len(in_block_bin), 32):
        in_block.append(hf.boolean.b_tonum(in_block_bin[i:i+32]))

    print(in_block)

    o = h.compute_md5(in_block)
    #print(o)

    return True

def __main__():
    tests = [tc_zero_block]

    for test in tests:
        ret = test()
        if ret:
            print(test.__name__ + "... OK")
        else:
            print(test.__name__ + "... Failed")
            break

if __name__ == "__main__":
    __main__()
