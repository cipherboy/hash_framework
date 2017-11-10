#!/usr/bin/env python3

def var_eval_and(expr, eval_table):
    assert(expr[0] == 'and')
    for i in range(1, len(expr)):
        r = var_eval(expr[i], eval_table)
        if r == 'F':
            return 'F'
    return 'T'

def var_eval_or(expr, eval_table):
    assert(expr[0] == 'or')
    for i in range(1, len(expr)):
        r = var_eval(expr[i], eval_table)
        if r == 'T':
            return 'T'
    return 'F'

def var_eval_xor(expr, eval_table):
    assert(expr[0] == 'xor')
    true = 0
    for i in range(1, len(expr)):
        r = var_eval(expr[i], eval_table)
        if r == 'T':
            true += 1
    if true % 2 == 0:
        return 'F'
    else:
        return 'T'

def var_eval(expr, eval_table):
    not_table = {'F': 'T', 'T': 'F'}
    if type(expr) == type(""):
        if expr in ['T', 'F']:
            return expr
        while expr in eval_table:
            expr = eval_table[expr]
        if expr in ['T', 'F']:
            return expr
    elif type(expr) == type((1, 2)):
        if len(expr) == 2 and expr[0] == 'not':
            if expr[1] in ['T', 'F']:
                return not_table[expr[1]]
            if expr[1] in eval_table:
                return not_table[eval_table[expr[1]]]
            return not_table[var_eval(expr[1], eval_table)]
        if len(expr) >= 3 and expr[0] == 'and':
            return var_eval_and(expr, eval_table)
        if len(expr) >= 3 and expr[0] == 'or':
            return var_eval_or(expr, eval_table)
        if len(expr) >= 3 and expr[0] == 'xor':
            return var_eval_xor(expr, eval_table)
    print(expr)
    return 1//0
