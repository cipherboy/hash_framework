import cmsh

"""
Simulate an ideal hash function: does the construct:

    output = iv + process(block, iv)

naturally elide collisions?
"""

def main():
    with cmsh.Model() as model:
        # Model IV as 4x 32-bit vectors
        iv_1 = model.vec(128)
        iv_2 = model.vec(128)
        iv_1s = model.split_vec(iv_1, 32)
        iv_2s = model.split_vec(iv_2, 32)

        # Model final state as random 4x 32-bit vectors
        final_1 = model.vec(128)
        final_2 = model.vec(128)
        final_1s = model.split_vec(final_1, 32)
        final_2s = model.split_vec(final_2, 32)

        # Model output state as sum of iv and final
        output_1s = [ iv_1s[i] + final_1s[i] for i in range(0, len(iv_1s)) ]
        output_2s = [ iv_2s[i] + final_2s[i] for i in range(0, len(iv_2s)) ]
        output_1 = model.join_vec(output_1s)
        output_2 = model.join_vec(output_2s)

        model.add_assert(output_1 == output_2)

        # Compute IV and Final deltas:
        iv_d = iv_1 ^ iv_2
        final_d = final_1 ^ final_2

        # With iv_d == 0, the only solution is final_d == 0; i.e., it is
        # sufficient to ignore the outer addition in this construction.
        #
        # For each iv_d non-zero, there may be one or more answers.
        model.add_assert(iv_d.bit_sum() == 0)

        count = 0
        while model.solve():
            print(bin(int(iv_d)), bin(int(final_d)))
            new_iv_d = iv_d != int(iv_d)
            new_final_d = final_d != int(final_d)

            model.add_assert(new_iv_d | new_final_d)
            count += 1

            if count % 100 == 0:
                print(count)

        print(count)


if __name__ == "__main__":
    main()
