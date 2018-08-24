import pytest

import hash_framework as hf
from hash_framework.boolean import *

MAX_VALUE = 64


def test_rca():
    for x in range(0, MAX_VALUE):
        for y in range(0, MAX_VALUE):
            x_bin = hf.boolean.b_tobitl(x)[-8:]
            y_bin = hf.boolean.b_tobitl(y)[-8:]
            s_bin = hf.boolean.b_tobitl(x+y)[-8:]
            out, _ = hf.boolean.b_rca("", x_bin, y_bin)
            if s_bin != out:
                print((x_bin, y_bin, s_bin, out))
            assert s_bin == out

    return True


def test_cla():
    for x in range(0, MAX_VALUE):
        for y in range(0, MAX_VALUE):
            x_bin = hf.boolean.b_tobitl(x)[-8:]
            y_bin = hf.boolean.b_tobitl(y)[-8:]
            s_bin = hf.boolean.b_tobitl(x+y)[-9:]
            out, c_out = hf.boolean.b_cla("", x_bin, y_bin, c='F')
            if s_bin != [c_out] + out:
                print((x_bin, y_bin, s_bin, out))
            assert s_bin == [c_out] + out
    return True


def test_csa():
    for x in range(0, MAX_VALUE):
        for y in range(0, MAX_VALUE):
            x_bin = hf.boolean.b_tobitl(x)[-8:]
            y_bin = hf.boolean.b_tobitl(y)[-8:]
            s_bin = hf.boolean.b_tobitl(x+y+1)[-9:]
            out, c_out = hf.boolean.b_csa("", x_bin, y_bin, c='T', adder_func=hf.boolean.b_rca)
            if s_bin != [c_out] + out:
                print((x_bin, y_bin, s_bin, out))
            assert s_bin == [c_out] + out
    return True
