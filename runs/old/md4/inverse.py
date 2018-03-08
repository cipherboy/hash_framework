import hash_framework as hf

def output_constraints(output):
    c = ['and']
    for key in output:
        for i in range(0, 32):
            c.append(('equal', "h" + key + str(i), output[key][i]))

    hf.models.vars.write_clause("coutput", tuple(c), "98-problem.txt")

def __main__():
    r = 20

    algo = hf.algorithms.md4()
    algo.rounds = r

    input_block = ['F'] * 512
    output = {}
    output['oaa'] = 'F'*32
    output['obb'] = 'F'*32
    output['occ'] = 'F'*32
    output['odd'] = 'F'*32

    m = hf.models()
    m.start("md4-inverse-r" + str(r), False)
    hf.models.vars.write_header()
    hf.models.generate(algo, ['h'], rounds=r, bypass=True)


    hf.models.vars.write_values(input_block, 'hb', "08-block.txt")
    output_constraints(output)


    hf.models.vars.write_assign(['coutput'])








__main__()
