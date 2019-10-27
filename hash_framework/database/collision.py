import cmsh

import hash_framework.algorithms as hfa

def _normalize_(model: cmsh.Model, obj):
    if isinstance(obj, cmsh.Vector):
        return int(obj)
    elif isinstance(obj, int):
        return obj
    elif isinstance(obj, (list, tuple)):
        obj = list(obj)
        for index, item in enumerate(obj):
            if isinstance(obj, cmsh.Vector):
                obj[index] = int(item)
            elif isinstance(obj, cmsh.Variable):
                obj[index] = bool(item)
        return model.join_vec(obj)
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
        for index, i_1 in enumerate(r_1):
            assert int(i_1) == int(r_2[index])

        assert block_1 != block_2

        assert block_1 != block_2 or iv_1 != iv_2

        if block_1 > block_2:
            return True
        if block_1 == block_2 and iv_1 > iv_2:
            return True
        return False

def save_collision(algo, model, block_1, iv_1, output_1, rounds_1, block_2, iv_2, output_2, rounds_2):
    swap = validate_collision(algo, model, block_1, iv_1, block_2, iv_2)
