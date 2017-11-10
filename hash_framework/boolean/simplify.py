#!/usr/bin/python

from hash_framework.boolean.translate import *

cache_simplify = {}

def simplify_and(expr):
    assert(expr[0] == 'and')
    result = ['and']

    for i in range(1, len(expr)):
        s = simplify(expr[i])
        if s == 'F':
            return 'F'
        if s == 'T':
            continue
        result.append(s)

    if len(result) == 1:
        return 'T'

    if len(result) == 2:
        return result[1]

    return tuple(result)

def simplify_or(expr):
    assert(expr[0] == 'or')
    result = ['or']

    for i in range(1, len(expr)):
        s = simplify(expr[i])
        if s == 'T':
            return 'T'
        if s == 'F':
            continue
        result.append(s)

    if len(result) == 1:
        return 'F'

    if len(result) == 2:
        return result[1]

    return tuple(result)

def simplify_xor(expr):
    assert(expr[0] == 'xor')
    result = ['xor']

    true = 0

    for i in range(1, len(expr)):
        s = simplify(expr[i])
        if s == 'T':
            true += 1
            continue
        if s == 'F':
            continue
        result.append(s)

    if len(result) == 1:
        if true % 2 == 0:
            return 'F'
        else:
            return 'T'

    if len(result) == 2:
        if true % 2 == 0:
            return result[1]
        else:
            return ('not', result[1])

    if true % 2 == 0:
        return tuple(result)
    else:
        return ('not', tuple(result))


def r_simplify(expr):
    sbmap = {'T': True, 'F': False}
    bsmap = {True: 'T', False: 'F'}
    if type(expr) != tuple:
        return expr
    if len(expr) == 2 and expr[0] == 'not':
        i_simplify = simplify(expr[1])
        if type(i_simplify) != tuple and i_simplify in ['T', 'F']:
            return bsmap[not sbmap[i_simplify]]
        if type(i_simplify) == tuple and i_simplify[0] == 'not':
            return simplify(i_simplify[1])
        return ('not', i_simplify)
    elif len(expr) >= 3 and expr[0] == 'and':
        return simplify_and(expr)
    elif len(expr) >= 3 and expr[0] == 'or':
        return simplify_or(expr)
    elif len(expr) >= 3 and expr[0] == 'xor':
        return simplify_xor(expr)
    print(expr)
    return 1/0

def simplify(expr):
    global cache_simplify
    if expr in cache_simplify:
        cache_simplify['hit'] = cache_simplify.get('hit', 0) + 1
        return cache_simplify[expr]
    cache_simplify[expr] = r_simplify(expr)
    cache_simplify['miss'] = cache_simplify.get('miss', 0) + 1
    return cache_simplify[expr]
