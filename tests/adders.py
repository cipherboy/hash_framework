#!/usr/bin/env python3

import hash_framework as hf
from hash_framework.boolean import *


def tc_rca():
    for x in range(0, 256):
        for y in range(0, 256):
            x_bin = hf.boolean.b_tobitl(x)[-8:]
            y_bin = hf.boolean.b_tobitl(y)[-8:]
            s_bin = hf.boolean.b_tobitl(x+y)[-8:]
            out, _ = hf.boolean.b_rca("", x_bin, y_bin)
            if s_bin != out:
                print((x_bin, y_bin, s_bin, out))
            assert(s_bin == out)

    return True

def tc_cla():
    for x in range(0, 256):
        for y in range(0, 256):
            x_bin = hf.boolean.b_tobitl(x)[-8:]
            y_bin = hf.boolean.b_tobitl(y)[-8:]
            s_bin = hf.boolean.b_tobitl(x+y)[-8:]
            out, _ = hf.boolean.b_cla("", x_bin, y_bin)
            if s_bin != out:
                print((x_bin, y_bin, s_bin, out))
            assert(s_bin == out)
    return True

def __main__():
    # tests = [tc_rca, tc_cla]
    tests = [tc_cla]

    for test in tests:
        ret = test()
        if ret:
            print(test.__name__ + "... OK")
        else:
            print(test.__name__ + "... Failed")
            break

if __name__ == "__main__":
    __main__()
