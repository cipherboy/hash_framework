import cmsh

import hash_framework.algorithms as hfa
import hash_framework.database as hfd

def _normalize_(model: cmsh.Model, obj):
    if isinstance(obj, cmsh.Vector):
        return int(obj)
    elif isinstance(obj, int):
        return obj
    elif isinstance(obj, (list, tuple)):
        obj = list(obj)
        all_vectors = True
        for index, item in enumerate(obj):
            if not isinstance(item, cmsh.Vector):
                all_vectors = False
        assert all_vectors
        return int(model.join_vec(obj))
    raise ValueError(f"Unknown type for object: {type(obj)}")

def validate_collision(algo, o_model, block_1, iv_1, block_2, iv_2):
    hf: hfa.md4 = hfa.fresh(algo)
    block_1 = _normalize_(o_model, block_1)
    iv_1    = _normalize_(o_model,    iv_1)
    block_2 = _normalize_(o_model, block_2)
    iv_2    = _normalize_(o_model,    iv_2)

    with cmsh.Model() as model:
        o_1, r_1 = hf.compute(model, block_1, iv=iv_1, rounds=algo.rounds)
        o_2, r_2 = hf.compute(model, block_2, iv=iv_2, rounds=algo.rounds)

        for index, i_1 in enumerate(o_1):
            assert int(i_1) == int(o_2[index])

        assert block_1 != block_2 or iv_1 != iv_2

        if block_1 > block_2:
            return True
        if block_1 == block_2 and iv_1 > iv_2:
            return True
        return False

def validate_output(algo, o_model, block, iv, output, rounds):
    hf: hfa.md4 = hfa.fresh(algo)
    block  = _normalize_(o_model,  block)
    iv     = _normalize_(o_model,    iv)
    output = _normalize_(o_model, output)
    rounds = _normalize_(o_model, rounds)

    with cmsh.Model() as model:
        output_a, rounds_a = hf.compute(model, block, iv=iv, rounds=algo.rounds)

        output_a = _normalize_(model, output_a)
        rounds_a = _normalize_(model, rounds_a)

        assert output_a == output
        assert rounds_a == rounds

def save_collision(db, algo, model, block_1, iv_1, output_1, rounds_1, block_2, iv_2, output_2, rounds_2, tag=None):
    swap = validate_collision(algo, model, block_1, iv_1, block_2, iv_2)
    validate_output(algo, model, block_1, iv_1, output_1, rounds_1)
    validate_output(algo, model, block_2, iv_2, output_2, rounds_2)

    if swap:
        tmp = (block_2, iv_2, output_2, rounds_2)
        block_2, iv_2, output_2, rounds_2 = (block_1, iv_1, output_1, rounds_1)
        block_1, iv_1, output_1, rounds_1 = tmp

    block_1  = _normalize_(model,  block_1)
    iv_1     = _normalize_(model,     iv_1)
    output_1 = _normalize_(model, output_1)
    rounds_1 = _normalize_(model, rounds_1)

    block_2  = _normalize_(model,  block_2)
    iv_2     = _normalize_(model,     iv_2)
    output_2 = _normalize_(model, output_2)
    rounds_2 = _normalize_(model, rounds_2)

    block_d = block_1 ^ block_2
    iv_d = iv_1 ^ iv_2
    output_d = output_1 ^ output_2
    rounds_d = rounds_1 ^ rounds_2

    cols = ['rounds']
    values = [algo.rounds]

    for column, value in algo.format(model, "h1_", block_1, iv_1, output_1, rounds_1).items():
        assert column not in cols
        cols.append(column)
        values.append(value)

    for column, value in algo.format(model, "h2_", block_2, iv_2, output_2, rounds_2).items():
        assert column not in cols
        cols.append(column)
        values.append(value)

    for column, value in algo.format(model, "d_", block_d, iv_d, output_d, rounds_d).items():
        assert column not in cols
        cols.append(column)
        values.append(value)

    assert len(cols) == len(values)

    create_table(db, algo)

    query = "INSERT INTO " + algo.name + "_collisions ("
    query += ", ".join(cols) + ") VALUES ("
    query += ", ".join(["?"] * len(cols))
    query += ")"
    return db.prepared(query, values)

def create_table(db, algo):
    cols = ["rounds"]
    cols.extend(hfd.get_columns(db, algo, "h1_"))
    cols.extend(hfd.get_columns(db, algo, "h2_"))
    cols.extend(hfd.get_columns(db, algo, "d_"))

    query = "CREATE TABLE IF NOT EXISTS " + algo.name + "_collisions ("
    query += ", ".join(map(lambda x: x + " TEXT", cols))
    query += ")"
    return db.execute(query)

