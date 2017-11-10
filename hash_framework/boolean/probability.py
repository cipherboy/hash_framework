#!/usr/bin/env python

cache_probability = {}

from decimal import *
getcontext().prec = 500

def r_probability(expr, probability_table):
    result = False
    if type(expr) == str and expr in probability_table:
        result = probability_table[expr]
    elif type(expr) == str and expr == 'F':
        result = Decimal(0.0)
    elif type(expr) == str and expr == 'T':
        result = Decimal(1.0)
    elif type(expr) == Decimal:
        result = expr
    elif type(expr) == tuple and len(expr) == 2 and expr[0] == 'not':
        result = Decimal(1) - probability(expr[1], probability_table)
    elif type(expr) == tuple and len(expr) == 3 and expr[0] == 'and':
        result = probability(expr[1], probability_table)*probability(expr[2], probability_table)
    elif type(expr) == tuple and len(expr) == 3 and expr[0] == 'or':
        result = Decimal(1) - ((Decimal(1) - probability(expr[1], probability_table))*(Decimal(1) - probability(expr[2], probability_table)))
    elif type(expr) == tuple and len(expr) == 3 and expr[0] == 'xor':
        result = ((Decimal(1) - probability(expr[1], probability_table))*(probability(expr[2], probability_table))) + ((probability(expr[1], probability_table))*(Decimal(1) - probability(expr[2], probability_table)))
    elif type(expr) == tuple and len(expr) == 3 and expr[0] == 'equal':
        result = probability(expr[1], probability_table)*probability(expr[2], probability_table) + (Decimal(1) - probability(expr[1], probability_table))*(Decimal(1) - probability(expr[2], probability_table))

    if result == False:
        return 1//0
    else:
        return result

def probability(expr, probability_table):
    global cache_probability
    if expr in cache_probability:
        cache_probability['hit'] = cache_probability.get('hit', 0) + 1
        return cache_probability[expr]
    cache_probability[expr] = r_probability(expr, probability_table)
    cache_probability['miss'] = cache_probability.get('miss', 0) + 1
    return cache_probability[expr]
