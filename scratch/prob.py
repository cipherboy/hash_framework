#!/usr/bin/env python3

import random

sr = random.SystemRandom()

def sample(prob):
    if sr.uniform(0, 1) <= (1 - prob):
        return False
    return True

def l_not(a):
    return not a

def l_and(a, b):
    return a and b

def l_or(a, b):
    return a or b

def l_xor(a, b):
    return l_or(l_and(a, b), l_and(l_not(a), l_not(b)))

def f(a, b, c):
    return l_or(l_and(a, b), l_or(l_and(a, c), l_and(b, c)))

def __main__():
    count = 1000000 * 10
    f_c = 0
    f_t = 0
    while f_t < count:
        ab = sample(0.5)
        c = sample(0.8)
        b = sample(0.8)

        if ab == True:
            b = True

        if l_and(b, c):
            f_c += 1
        f_t += 1

    print(f_c / f_t)

if __name__ == "__main__":
    __main__()
