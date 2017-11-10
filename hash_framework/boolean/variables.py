#!/usr/bin/python

from hash_simplify import *

cache_find = {}
cache_count = {}
cache_replace = {}

def var_find_r(expr):
    if type(expr) == type((1, 2)) and len(expr) == 2 and expr[0] == 'not':
        if type(expr[1]) == type(""):
            return set([expr[1]])
        return var_find(expr[1])
    elif type(expr) == type((1, 2)) and len(expr) >= 3 and expr[0] in ['and', 'or', 'xor']:
        base = set()
        for i in range(1, len(expr)):
            r = set([expr[i]])
            if type(expr[i]) != type(""):
                r = var_find(expr[i])

            base.update(r)
        return base
    elif expr in ['T', 'F']:
        return set()
    elif type(expr) == type(""):
        return set([expr])
    print(expr)
    return 1//0

def var_find(expr):
    global cache_find
    if expr in cache_find:
        return cache_find[expr]

    cache_find[expr] = var_find_r(expr)

    return cache_find[expr]

def var_count_r(expr):
    return len(var_find(expr))

def var_count(expr):
    global cache_count
    if expr in cache_count:
        return cache_count[expr]

    cache_count[expr] = var_count_r(expr)

    return cache_count[expr]

def var_replace(expr, eval_table):
    if type(expr) == type((1, 2)) and len(expr) == 2:
        return simplify((expr[0], var_replace(expr[1], eval_table)))
    elif type(expr) == type((1, 2)) and len(expr) == 3:
        return simplify((expr[0], var_replace(expr[1], eval_table), var_replace(expr[2], eval_table)))
    if expr in ['T', 'F']:
        return expr
    elif expr in eval_table:
        return eval_table[expr]
    return expr

def var_evaluate(vars):
    solved = {}
    for i in vars:
        if vars[i] in ['T', 'F']:
            solved[i] = vars[i]
    while not solved == set(vars.keys()):
        found = False
        for i in vars:
            if not vars[i] in ['T', 'F']:
                vars[i] = var_replace(vars[i], solved)
                found = True
                if vars[i] in ['T', 'F']:
                    solved[i] = vars[i]
            else:
                if i not in solved:
                    found = True
                    solved.add(i)
        if not found:
            break
    return vars
