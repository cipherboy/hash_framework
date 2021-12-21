#!/usr/bin/python3

import itertools
import functools

import cmsh

import hash_framework.algorithms as hfa
import hash_framework.database as hfd
import hash_framework.utils as hfu

ALGO = 'md4'

def check_block_delta_candidate(block_delta_i):
    with cmsh.Model() as model:
        hf: hfa.md4 = hfa.resolve(ALGO)

        # Ensure our delta is valid.
        block_delta = model.to_vec(block_delta_i, hf.block_size)

        # First construct two blocks with the given delta.
        block_1 = model.vec(hf.block_size)
        block_2 = model.vec(hf.block_size)
        model.add_assert((block_1 ^ block_2) == block_delta)

        # Assume we have any possible iv. This is safe even in the case
        # that iv_1 == iv_2 and our delta doesn't align with the blocks
        # under test (3, 11, 7, or 15), because we later calculate the
        # last possible round where we could have a difference and still
        # collide.
        iv_1 = model.vec(hf.state_size)
        iv_2 = model.vec(hf.state_size)

        # Compute the last 4 rounds and check if this is a viable candidate
        # (that we can generate a collision with).
        output_1s, _ = hf.eval(model, block_1, iv=iv_1, rounds=range(hf.rounds - 4, hf.rounds))
        output_2s, _ = hf.eval(model, block_2, iv=iv_2, rounds=range(hf.rounds - 4, hf.rounds))
        output_1 = model.join_vec(output_1s)
        output_2 = model.join_vec(output_2s)
        model.add_assert(output_1 == output_2)

        assert model.solve()

def last_possible_round(block_delta_i):
    with cmsh.Model() as model:
        hf: hfa.md4 = hfa.resolve(ALGO)

        # Ensure our delta is valid and split it into block-sized chunks.
        block_delta = model.to_vec(block_delta_i, hf.block_size)
        block_deltas = model.split_vec(block_delta, hf.block_size // hf.blocks)
        last_round = 0

        delta_indices = set()

        for round_num, block_index in enumerate(hf.block_schedule):
            if int(block_deltas[block_index]) != 0:
                delta_indices.add(block_index)
                last_round = round_num

        assert last_round != 0

        return tuple(delta_indices), last_round

def load_known_pieces(db, hf, block_delta_i):
    with cmsh.Model() as model:
        # Split into block-sized chunks so we can iterate over database data
        # and check if it is relevant for this solving session.
        block_delta = model.split_vec(model.to_vec(block_delta_i, hf.block_size), hf.block_size // hf.blocks)

        table_name = hf.name + "_collision_pieces"
        cols = ['round', 'h1_state', 'h2_state', 'd_state', 'h1_block',
                'h2_block', 'd_block', 'h1_output', 'h2_output', 'd_output']
        for row in db.query(table_name, cols):
            row['round'] = int(row['round'])
            round_num = row['round']
            block_index = hf.block_schedule[round_num]
            d_block = hex(int(block_delta[block_index]))[2:]

            if row['d_block'] != d_block:
                continue

            yield row

def organize_pieces(hf, pieces):
    result = {}
    for round_num in range(hf.rounds):
        result[round_num] = []

    for piece in pieces:
        add_piece(result, piece)

    return result

def add_piece(result, piece):
    round_num = piece['round']
    found = False
    for entry in result[round_num]:
        if piece['d_state'] == entry['d_state'] and piece['d_block'] == entry['d_block'] and piece['d_output'] == entry['d_output']:
            found = True
            break

    if not found:
        result[round_num].append(piece)

    return result

def iterate_differentials(hf, width=None, max_number=None):
    if width is None:
        width = hf.int_size + 1
    if max_number is None:
        max_number = hf.int_size

    for num_delta_bits in range(width):
        for diff_bits in itertools.combinations(range(max_number), num_delta_bits):
            differential = 0
            for bit in diff_bits:
                differential |= (1 << bit)
            yield differential

def iv_delta(hf, round_num, iv_delta_constraints):
    if iv_delta_constraints[round_num] is not None:
        return (iv_delta_constraints[round_num],)

    return iterate_differentials(hf, 128, 5)

def piece_args_gen(hf, block_delta, iv_delta_constraints, iv_h1_value_constraints, iv_h2_value_constraints):
    for round_num in range(hf.rounds):
        for output_bits in range(hf.int_size):
            for this_iv_delta in iv_delta(hf, round_num, iv_delta_constraints):
                yield (round_num, block_delta, this_iv_delta, iv_h1_value_constraints[round_num], iv_h2_value_constraints[round_num])

def find_single_piece(round_num, block_delta_i, iv_delta_constraint, iv_h1_value_constraint, iv_h2_value_constraint):
    """
    Without any regard for whether this fits together, find a bunch of
    individual pieces (single rounds) we can try and piece together later.
    We still need to comply with the input constraints (block delta,
    iv_delta, and fixed iv_values) though.
    """
    with cmsh.Model() as model:
        hf: hfa.md4 = hfa.resolve(ALGO)

        # Use any iv and refine according to input constraints.
        iv_1 = model.vec(hf.state_size)
        iv_2 = model.vec(hf.state_size)
        if iv_delta_constraint:
            model.add_assert((iv_1 ^ iv_2) == model.to_vec(iv_delta_constraint, hf.state_size))
        if iv_h1_value_constraint:
            constraint = model.join_vec(
                map(
                    lambda v: model.to_vec(v, hf.int_size),
                    iv_h1_value_constraint
                )
            )
            model.add_assert(iv_1 == constraint)
        if iv_h2_value_constraint:
            constraint = model.join_vec(
                map(
                    lambda v: model.to_vec(v, hf.int_size),
                    iv_h2_value_constraint
                )
            )
            model.add_assert(iv_2 == constraint)

        # Create a block according to the specified block delta.
        block_delta = model.to_vec(block_delta_i, hf.block_size)
        block_1 = model.vec(hf.block_size)
        block_2 = model.vec(hf.block_size)
        model.add_assert((block_1 ^ block_2) == block_delta)

        # Finally, compute a single round.
        output_1s, rounds_1s = hf.eval(model, block_1, iv=iv_1, rounds=[round_num])
        output_2s, rounds_2s = hf.eval(model, block_2, iv=iv_2, rounds=[round_num])
        output_1 = model.join_vec(output_1s)
        output_2 = model.join_vec(output_2s)
        round_1 = model.join_vec(rounds_1s)
        round_2 = model.join_vec(rounds_2s)

        _ = iv_1 ^ iv_2
        _ = block_1 ^ block_2
        _ = output_1 ^ output_2
        model.add_assert((round_1 ^ round_2).bit_sum() <= 5)

        assert len(round_1) == hf.int_size
        assert len(round_2) == hf.int_size

        discovered = []
        while model.solve(max_time=1) is True:
            if not model.sat:
                continue
            discovered.append({
                'round': round_num,
                'h1_state': hex(int(iv_1))[2:],
                'h2_state': hex(int(iv_2))[2:],
                'd_state': hex(int(iv_1) ^ int(iv_2))[2:],
                'h1_block': hex(int(block_1))[2:],
                'h2_block': hex(int(block_2))[2:],
                'd_block': hex(int(block_1) ^ int(block_2))[2:],
                'h1_output': hex(int(output_1))[2:],
                'h2_output': hex(int(output_2))[2:],
                'd_output': hex(int(output_1) ^ int(output_2))[2:],
            })
            negated = model.negate_solution(round_1 ^ round_2)
            model.add_assert(negated)

            if len(discovered) >= 128:
                # Arbitrary cutoff to prevent individual tasks from running
                # too long.
                break
        return discovered

def piece_count(known_pieces):
    count = 0
    for block in known_pieces:
        count += len(known_pieces[block])
    return count

def main():
    # Grab a hash algorithm instance so we can initialize our database.
    hf: hfa.md4 = hfa.resolve(ALGO)

    # Initialize our database to generate collisions and store intermediate
    # round results.
    db = hfd.Database("~/hf/round.db")
    hfd.create_table(db, hf)

    # User-supplied block differential.
    block_delta = 1 << 511

    # First check that the given block delta can produce collisions in the
    # last few rounds.
    check_block_delta_candidate(block_delta)

    # Then compute the exact final target round; after this round, the blocks
    # have no difference so we need to have reached zero state delta by then.
    delta_indices, last_round = last_possible_round(block_delta)
    print(delta_indices, last_round)

    # These constraints allow user-supplied assumptions in parallel to
    # discovered constraints.
    iv_delta_constraints = [None] * hf.rounds
    iv_h1_value_constraints = [None] * hf.rounds
    iv_h2_value_constraints = [None] * hf.rounds

    # User-supplied assumption: The first round's IV is the default, and thus
    # thus the delta is 0.
    iv_delta_constraints[0] = 0
    iv_h1_value_constraints[0] = hf.default_state
    iv_h2_value_constraints[0] = hf.default_state

    # Load existing knowledge from the database.
    print("Loading existing pieces from the database...")
    known_pieces = organize_pieces(hf, load_known_pieces(db, hf, block_delta))
    print(f"Got {piece_count(known_pieces)} pieces")

    # Create a single generator instance for creating arguments to solve for
    # valid differential pieces.
    piece_generator = piece_args_gen(hf, block_delta, iv_delta_constraints, iv_h1_value_constraints, iv_h2_value_constraints)

    # Assume the user will hit Ctrl+C when we've run for long enough.
    while True:
        # Start by solving for new pieces that could augment our
        new_process_pieces = hfu.parallel_run(find_single_piece, piece_generator, items_to_process=100)
        for process_pieces in new_process_pieces:
            for piece in process_pieces:
                print(piece)
                added = add_piece(known_pieces, piece)
                if added:
                    store_piece(piece)


if __name__ == "__main__":
    main()
