def table_cols(algo):
    if algo.name == "md4" or algo.name == "md5":
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
    elif algo.name == "sha3":
        cols = ["i", "o"]
        for i in range(0, algo.rounds):
            cols.append("r1t" + str(i))
            cols.append("r1r" + str(i))
            cols.append("r1p" + str(i))
            cols.append("r1c" + str(i))
            cols.append("r1i" + str(i))
        return cols
    print("Unknown algorithm")
    raise
