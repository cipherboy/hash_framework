import hash_framework
import sys

def get_rowid_count(db, algo):
    q = "SELECT COUNT(ROWID) from c_" + algo.name
    q += " WHERE tag='' or tag is null;"
    datas = db.execute(q).fetchall()
    return datas[0][0]

def get_rows(db, algo):
    cols = hash_framework.attacks.collision.table_cols(algo)
    cols.append("tag")
    cols.append("ROWID")

    q = "SELECT " + ','.join(cols) + " FROM c_" + algo.name
    q += " WHERE ROWID in ("
    q += "    SELECT ROWID from c_" + algo.name
    q += "    WHERE tag='' or tag is null LIMIT 10000);"

    datas = db.execute(q).fetchall()
    results = []
    for data in datas:
        r = {}
        for i in range(0, len(cols)):
            r[cols[i]] = data[i]
        results.append(r)
    return results


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

def retag(db, algo, r):
    tag = determine_tag(algo, r)
    rowid = r['ROWID']

    q = "UPDATE c_" + algo.name
    q += " SET tag='" + tag + "' WHERE ROWID="+str(rowid) + ";"
    db.execute(q, commit=False, rowid=False)


def __main__():
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " algorithm")
        return

    db = hash_framework.database()
    algo = hash_framework.algorithms.lookup(sys.argv[1])()
    rowids = get_rowid_count(db, algo)
    print(rowids)
    while rowids > 0:
        rows = get_rows(db, algo)
        for row in rows:
            retag(db, algo, row)
        rowids = get_rowid_count(db, algo)
        print(rowids)
    db.commit()


if __name__ == "__main__":
    __main__()
