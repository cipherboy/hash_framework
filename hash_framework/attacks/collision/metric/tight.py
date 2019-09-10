def distance(algo, col1, col2):
    r = 0
    for i in range(0, algo.rounds):
        k = "di" + str(i)
        if col1[k] != col2[k]:
            r += 1
    return r


def delta(algo, col1, col2):
    r = []
    for i in range(0, algo.rounds):
        k = "di" + str(i)
        if col1[k] != col2[k]:
            r.append((i, col1[k], col2[k]))
    return r
