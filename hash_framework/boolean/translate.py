#!/usr/bin/python

cache_translate = {}
cache_clause_reduce = {}
cache_clause_dedupe = {}

clause_count = {}
clause_dedupe_s = {}
cache_rename = {}

def var_rename_r(expr, eval_table):
    if type(expr) == str:
        if expr in ['T', 'F']:
            return expr
        if expr in eval_table:
            return eval_table[expr]
        return expr
    if type(expr) == tuple and len(expr) >= 2:
        c = [expr[0]]
        for i in expr[1:]:
            c.append(var_rename(i, eval_table))
        return tuple(c)
    print(expr)
    return 1//0

def var_rename(expr, eval_table):
    global cache_rename
    if expr in cache_rename:
        return cache_rename[expr]
    cache_rename[expr] = var_rename_r(expr, eval_table)
    return cache_rename[expr]

def is_var_expr(expr):
    if type(expr) == str:
        return True
    return False

def clause_dedupe_r(expr, prefix):
    global clause_dedupe_s
    global clause_count
    if is_var_expr(expr):
        return expr
    if type(expr) == tuple and expr[0] == 'not' and len(expr) == 2:
        l_v = expr[1]
        if not is_var_expr(l_v):
            l_v = clause_dedupe(expr[1], prefix)
        name = prefix + "t" + str(clause_count[prefix])
        clause_dedupe_s[name] = (expr[0], l_v)
        clause_count[prefix] += 1
        return name

    if type(expr) == tuple and len(expr) >= 3:
        r = [expr[0]]
        for i in range(1, len(expr)):
            v = expr[i]
            if not is_var_expr(v):
                v = clause_dedupe(v, prefix)
            r.append(v)

        name = prefix + "t" + str(clause_count[prefix])
        clause_dedupe_s[name] = tuple(r)
        clause_count[prefix] += 1

        return name

    print(expr)

    return 1//0

def clause_dedupe(expr, prefix):
    if prefix not in clause_count:
        clause_count[prefix] = 1
    global cache_clause_dedupe
    if (expr, prefix) in cache_clause_dedupe:
        return cache_clause_dedupe[(expr, prefix)]
    cache_clause_dedupe[(expr, prefix)] = clause_dedupe_r(expr, prefix)
    return cache_clause_dedupe[(expr, prefix)]

def clause_dedupe_cache():
    global clause_dedupe_s
    return clause_dedupe_s

def clause_reduce_r(expr):
    if type(expr) != tuple:
        return expr
    result = [expr[0]]
    for c in expr[1:]:
        reduced = clause_reduce(c)
        if reduced[0] != expr[0]:
            result.append(reduced)
        else:
            for sub in reduced[1:]:
                result.append(sub)
    return tuple(result)

def clause_reduce(expr):
    global cache_clause_reduce
    if expr in cache_clause_reduce:
        return cache_clause_reduce[expr]
    cache_clause_reduce[expr] = clause_reduce_r(expr)
    return cache_clause_reduce[expr]

def translate_r(expr):
    if type(expr) != tuple:
        return expr
    if len(expr) == 2 and expr[0] == 'not':
        return "NOT(" + translate(expr[1]) + ")"
    if len(expr) == 3 and expr[0] == 'equal':
        s = "(" + translate(expr[1]) + " == " + translate(expr[2]) + ")"
        return s
    if len(expr) >= 2 and expr[0] == 'and':
        s = "AND("
        for c in expr[1:]:
            s += translate(c) + ","
        s = s[:-1] + ")"
        return s
    if len(expr) >= 2 and expr[0] == 'or':
        s = "OR("
        for c in expr[1:]:
            s += translate(c) + ","
        s = s[:-1] + ")"
        return s
    if len(expr) >= 2 and expr[0] == 'xor':
        s = "ODD("
        for c in expr[1:]:
            s += translate(c) + ","
        s = s[:-1] + ")"
        return s
    print(expr[0])
    print(len(expr))
    return 1/0

def translate(expr):
    global cache_translate
    if expr in cache_translate:
        return cache_translate[expr]
    cache_translate[expr] = translate_r(expr)
    return cache_translate[expr]
