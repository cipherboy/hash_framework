import hash_framework
import sys

def get_rowids(db, algo):
    q = "SELECT ROWID from c_" + algo.name
    q += " WHERE tag='' or tag is null;"
    rowids = set()
    datas = db.execute(q).fetchall()
    for data in datas:
        rowids.add(data[0])
    return rowids

def determine_tag(algo, row):
    rounds = 0
    base = '.'*32
    deltas = []
    for i in range(0, algo.rounds):
        k = "ri" + str(i)
        if k in row and row[k] != None:
            rounds = i+1
            if row[k] != base:
                deltas.append(i)
    tag = "md4-r" + str(rounds) + "-e" + '-'.join(map(str, deltas))
    return tag

def retag(db, algo, rowid):
    name = "c_" + algo.name
    cols = hash_framework.attacks.collision.table_cols(algo)
    cols.append("tag")

    r = db.query(name, cols, rowid=rowid, limit=1)
    tag = determine_tag(algo, r)
    r['tag'] = tag

    q = "UPDATE c_" + algo.name
    q += " SET tag='" + tag + "' WHERE ROWID="+str(rowid) + ";"
    db.execute(q, commit=False, rowid=False)


def __main__():
    db = hash_framework.database()
    algo = hash_framework.algorithms.lookup(sys.argv[1])()
    rowids = get_rowids(db, algo)
    print(len(rowids))
    for rowid in rowids:
        retag(db, algo, rowid)
    db.commit()


if __name__ == "__main__":
    __main__()
