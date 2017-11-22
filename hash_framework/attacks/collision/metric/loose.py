def distance(algo, col1, col2):
    r = 0
    for i in range(0, algo.rounds):
        k = "ri" + str(i)
        if col1[k] != col2[k]:
            r += 1
    return r

def delta(algo, col1, col2):
    r = []
    for i in range(0, algo.rounds):
        k = "ri" + str(i)
        if col1[k] != col2[k]:
            r.append((i, col1[k], col2[k]))
    return r

def delta_alt(rounds, col1, col2):
    r = []
    for i in range(0, rounds):
        if col1[i] != col2[i]:
            r.append(i)
    return r

def abs(algo, col):
    r = []
    for i in range(0, algo.rounds):
        k = "ri" + str(i)
        if col[k] != '.'*32:
            r.append(i)
    return tuple(r)
