from hash_framework import attacks
from hash_framework.models import models


def get_block_round_funcs(algo, index):
    i = int(index)
    result = []
    rounds = algo.block_map[i]
    for round in rounds:
        result.append(algo.round_funcs[round])
    return result


def apply_round_funcs(algo, round_funcs, args):
    r = []
    assert len(round_funcs) == len(args)
    for i in range(0, len(round_funcs)):
        round_func = round_funcs[i]
        arg = args[i]
        r.append(round_func(arg[0], arg[1], arg[2], arg[3]))
    return r


def round_to_eval_table(eval_table, rounds, prefixes):
    assert len(rounds) == len(prefixes)
    for i in range(0, len(rounds)):
        r = rounds[i]
        prefix = prefixes[i]
        for j in range(0, len(r)):
            eval_table[prefix + str(j)] = r[j]
    return eval_table
