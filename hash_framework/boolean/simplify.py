#!/usr/bin/python

from hash_translate import *

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
    if type(expr) != type((1, 2)):
        return expr
    if len(expr) == 2 and expr[0] == 'not':
        i_simplify = simplify(expr[1])
        if type(i_simplify) != type((1, 2)) and i_simplify in ['T', 'F']:
            return bsmap[not sbmap[i_simplify]]
        if type(i_simplify) == type((1, 2)) and i_simplify[0] == 'not':
            return simplify(i_simplify[1])
        return ('not', i_simplify)
    elif len(expr) >= 3 and expr[0] == 'and':
        return simplify_and(expr)
        l_simplify = simplify(expr[1])
        r_simplify = simplify(expr[2])

        if l_simplify == 'F' or r_simplify == 'F':
            return 'F'
        if l_simplify == 'T' and r_simplify == 'T':
            return 'T'
        if l_simplify == 'T':
            return r_simplify
        if r_simplify == 'T':
            return l_simplify
        if l_simplify == r_simplify:
            return l_simplify
        if l_simplify[0] == 'not' and l_simplify[1] == r_simplify:
            return 'F'
        if r_simplify[0] == 'not' and r_simplify[1] == l_simplify:
            return 'F'
        if l_simplify[0] == 'or' and r_simplify[0] == 'or' and l_simplify[1] == r_simplify[1]:
            return simplify(('or', l_simplify[1], ('and', l_simplify[2], r_simplify[2])))
        if l_simplify[0] == 'or' and r_simplify[0] == 'or' and l_simplify[2] == r_simplify[1]:
            return simplify(('or', l_simplify[2], ('and', l_simplify[1], r_simplify[2])))
        if l_simplify[0] == 'or' and r_simplify[0] == 'or' and l_simplify[1] == r_simplify[2]:
            return simplify(('or', l_simplify[1], ('and', l_simplify[2], r_simplify[1])))
        if l_simplify[0] == 'or' and r_simplify[0] == 'or' and l_simplify[2] == r_simplify[2]:
            return simplify(('or', l_simplify[2], ('and', l_simplify[1], r_simplify[1])))
        if l_simplify[0] == 'not' and r_simplify[0] == 'not':
            return simplify(('not', ('or', l_simplify[1], r_simplify[1])))
        return ('and', l_simplify, r_simplify)
    elif len(expr) >= 3 and expr[0] == 'or':
        return simplify_or(expr)
        l_simplify = simplify(expr[1])
        r_simplify = simplify(expr[2])

        if l_simplify == 'F' and r_simplify == 'F':
            return 'F'
        if l_simplify == 'T' or r_simplify == 'T':
            return 'T'
        if l_simplify == 'F':
            return r_simplify
        if r_simplify == 'F':
            return l_simplify
        if l_simplify == r_simplify:
            return l_simplify
        if l_simplify[0] == 'not' and l_simplify[1] == r_simplify:
            return 'T'
        if r_simplify[0] == 'not' and r_simplify[1] == l_simplify:
            return 'T'
        if l_simplify[0] == 'and' and r_simplify[0] == 'and' and l_simplify[1] == r_simplify[1]:
            return simplify(('and', l_simplify[1], ('or', l_simplify[2], r_simplify[2])))
        if l_simplify[0] == 'and' and r_simplify[0] == 'and' and l_simplify[2] == r_simplify[1]:
            return simplify(('and', l_simplify[2], ('or', l_simplify[1], r_simplify[2])))
        if l_simplify[0] == 'and' and r_simplify[0] == 'and' and l_simplify[1] == r_simplify[2]:
            return simplify(('and', l_simplify[1], ('or', l_simplify[2], r_simplify[1])))
        if l_simplify[0] == 'and' and r_simplify[0] == 'and' and l_simplify[2] == r_simplify[2]:
            return simplify(('and', l_simplify[2], ('or', l_simplify[1], r_simplify[1])))
        if l_simplify[0] == 'not' and r_simplify[0] == 'not':
            return ('not', ('and', l_simplify[1], r_simplify[1]))
        return ('or', l_simplify, r_simplify)
    elif len(expr) >= 3 and expr[0] == 'xor':
        return simplify_xor(expr)
        l_simplify = simplify(expr[1])
        r_simplify = simplify(expr[2])

        if l_simplify == r_simplify:
            return 'F'
        if l_simplify == 'T' and r_simplify == 'F':
            return 'T'
        if l_simplify == 'F' and r_simplify == 'T':
            return 'T'
        if l_simplify == 'T':
            return simplify(('not', r_simplify))
        if l_simplify == 'F':
            return r_simplify
        if r_simplify == 'T':
            return simplify(('not', l_simplify))
        if r_simplify == 'F':
            return l_simplify
        if l_simplify[0] == 'not' and l_simplify[1] == r_simplify:
            return 'T'
        if r_simplify[0] == 'not' and r_simplify[1] == l_simplify:
            return 'T'
        if l_simplify[0] == 'not' and r_simplify[0] == 'not':
            return ('xor', l_simplify[1], r_simplify[1])
        return ('xor', l_simplify, r_simplify)
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
