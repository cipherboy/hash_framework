import cmsh

import hash_framework.algorithms as hfa
import hash_framework.database as hfd
import hash_framework.utils as hfu

def test_get_columns():
    db = hfd.Database(":memory:")
    algo = hfa.md4()
    assert hfd.get_columns(db, algo)

    prefixed = hfd.get_columns(db, algo, "something")
    for item in prefixed:
        assert item.startswith("something")

    db.close()

def test_save_collision():
    with cmsh.Model() as model:
        hf = hfa.resolve('md4')

        k1 = "839c7a4d7a92cb5678a5d5b9eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edd45e51fe39708bf9427e9c3e8b9"
        k2 = "839c7a4d7a92cbd678a5d529eea5a7573c8a74deb366c3dc20a083b69f5d2a3bb3719dc69891e9f95e809fd7e8b23ba6318edc45e51fe39708bf9427e9c3e8b9"

        assert k1 != k2

        known_shaped_1 = list(map(lambda x: model.to_vector(x, width=32), hfa.split_hex(k1, 8)))
        known_shaped_2 = list(map(lambda x: model.to_vector(x, width=32), hfa.split_hex(k2, 8)))

        block_1 = model.vec(hf.block_size)
        block_2 = model.vec(hf.block_size)

        output_1s, rounds_1s = hf.compute(model, block_1)
        output_2s, rounds_2s = hf.compute(model, block_2)

        output_1 = model.join_vec(output_1s)
        output_2 = model.join_vec(output_2s)

        rounds_1 = model.join_vec(rounds_1s)
        rounds_2 = model.join_vec(rounds_2s)

        model.add_assert(block_1 < block_2)
        model.add_assert(block_1 == model.join_vec(known_shaped_1))
        model.add_assert(block_2 == model.join_vec(known_shaped_2))
        model.add_assert(output_1 == output_2)

        assert model.solve()
        assert int(output_1) == int(output_2)

        db = hfd.Database(":memory:")
        default_state = model.join_vec(
            map(
                lambda x: model.to_vec(x, 32),
                hf.default_state
            )
        )
        hfd.save_collision(db, hf, model, block_1, default_state, output_1, rounds_1, block_2, default_state, output_2, rounds_2)
        db.close()
