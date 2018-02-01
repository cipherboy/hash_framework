import hash_framework
import functools, random
import itertools

def __main__():
    pass

def get_differential_families(db, name, r):
    c = []
    for i in range(0, 16):
        c.append('rb' + str(i))
    q = "SELECT DISTINCT " + ','.join(c) + " FROM c_" + name + " WHERE tag LIKE '%" + str(r) + "%';"
    dset = set()
    datas = db.execute(q).fetchall()
    for data in datas:
        t = []
        for i in range(0, 16):
            if data[i] != '.'*32:
                t.append(i)
        dset.add(tuple(t))
    print(len(dset))
    return dset


def rank_differentials(db, name, r):
    max_count = 0
    results = {}
    for p in get_differential_families(db, name, r):
        c = []
        for i in range(0, 16):
            if i in p:
                c.append('rb' + str(i) + '!="' + '.'*32 + '"')
            else:
                c.append('rb' + str(i) + '="' + '.'*32 + '"')
        clause = ' AND '.join(c)
        q = "SELECT COUNT(DISTINCT(tag)) FROM c_" + name + " WHERE " + clause + ";"
        count = db.execute(q).fetchone()
        if count[0] > 0:
            results[p] = count[0]
            if count[0] > max_count:
                max_count = count[0]
                print((p, count[0]))

    print(results)

if __name__ == "__main__":
    db = hash_framework.database()

    rank_differentials(db, 'md4', 24)
