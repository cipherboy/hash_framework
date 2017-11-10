from hash_framework import attacks
from hash_framework import models

def analyze(algo, cols, prefix='h1'):
    assert(type(prefix) == str)
    stuck = []
    for r in range(0, algo.rounds):
        e = prefix + "i" + str(r)
        for i in range(0, algo.int_size):
            v = set()
            for col in cols:
                v.add(col[e][i])
                if len(v) == 2:
                    break
            if len(v) == 1:
                stuck.append((prefix, 'i', r, i, list(v)[0]))
    return stuck

def try_invalidate(algo, db, stucks):
    m = models()
    for stuck in stucks:
        n = '-'.join(map(str, stuck))
        s_n = stuck[0] + stuck[1] + str(stuck[2]*algo.int_size + stuck[3])
        s_v = stuck[4]
        cols = attacks.collision.load_db_tag(algo, db, "md4-wangs-original")
        tag = "md4-wangs-stuck-state-" + n
        m.start(tag, False)
        attacks.collision.loose.model(algo, m, cols, True)
        models.vars.write_clause('cstuck', ('not', ('equal', s_n, s_v)), '25-stuck.txt')
        models.vars.write_assign(['ccollision', 'cblocks', 'cdifferentials', 'cstuck', 'cstate'])
        m.collapse()
        m.build()
        m.run(count=10)
        rs = m.results(algo)
        attacks.collision.insert_db_multiple(algo, db, rs, tag)

def try_invalidate_independent(algo, db, stucks):
    m = models()
    for stuck in stucks:
        n = '-'.join(map(str, stuck))
        s_n = stuck[0] + stuck[1] + str(stuck[2]*algo.int_size + stuck[3])
        s_v = stuck[4]
        cols = attacks.collision.load_db_tag(algo, db, "md4-wangs-original")
        tag = "md4-wangs-stuck-state-independent-" + n
        m.start(tag, False)
        attacks.collision.loose.model(algo, m, cols, True)
        os.system("rm 01-h1-state.txt")
        os.system("rm 01-h2-state.txt")
        models.vars.write_clause('cstuck', ('not', ('equal', s_n, s_v)), '25-stuck.txt')
        models.vars.write_assign(['ccollision', 'cblocks', 'cdifferentials', 'cstuck', 'cstate'])
        m.collapse()
        m.build()
        m.run(count=10)
        rs = m.results(algo)
        attacks.collision.insert_db_multiple(algo, db, rs, tag)

def write(algo, stucks, name="08-stuck.txt"):
    s = ['and']
    for stuck in stucks:
        s_n = stuck[0] + stuck[1] + str(stuck[2]*algo.int_size + stuck[3])
        s_v = stuck[4]
        s.append(('equal', s_n, s_v))
    models.vars.write_clause('cstuck', tuple(s), name)
