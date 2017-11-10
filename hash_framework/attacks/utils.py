def table_cols(algo):
    cols = []
    for i in range(0, algo.state_size//algo.int_size):
        cols.append("s" + str(i))
    for i in range(0, algo.block_size//algo.int_size):
        cols.append("b" + str(i))
    for i in range(0, algo.rounds):
        cols.append("i" + str(i))
    for i in range(0, algo.state_size//algo.int_size):
        cols.append("o" + str(i))
    return cols
