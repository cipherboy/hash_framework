from hash_framework.attacks import *
from hash_framework.attacks.collision.metric.loose import abs as loose_abs

from hash_framework.attacks.utils import table_cols as attacks_table_cols
from hash_framework.database import database
from hash_framework.models import models
from hash_framework.utils import *

import sqlite3

def import_from_other(db, algo, path):
    db2 = database()
    db2.path=path
    db2.conn = sqlite3.connect(db2.path)
    cols = load_db(algo, db2)
    print(len(cols))
    import_db_multiple(algo, db, cols)

def import_from_other_tag(path, tag):
    db2 = database()
    db2.path=path
    db2.conn = sqlite3.connect(db2.path)
    cols = load_db_tag(algo, db2, tag)
    print(len(cols))
    insert_db_multiple(algo, db, cols, tag)

def create_table(algo, db):
    q = create_table_query(algo, db_type=db.type)
    db.execute(q, limit=1)

def clean_table(algo, db):
    cols = table_cols(algo)
    cols.append("tag")
    q = "CREATE TABLE cleaning_c_" + algo.name + " AS SELECT min(ROWID),"
    q += ','.join(cols)
    q += " FROM c_" + algo.name + " GROUP BY "
    q += ','.join(cols)
    q += ";"
    print(q)
    #db.execute(q)
    q = "ALTER TABLE c_" + algo.name + " RENAME TO backup_c_" + algo.name + ";"
    print(q)
    #db.execute(q)
    q = "CREATE TABLE c_" + algo.name + " AS SELECT "
    q += ','.join(cols)
    q += " FROM cleaning_c_" + algo.name + " GROUP BY "
    q += ','.join(cols)
    q += ";"
    print(q)
    #db.execute(q)

    print("Done")

def table_cols(algo):
    cols = []
    bare_cols = attacks_table_cols(algo)
    prefixes = ["h1", "h2", "d", "r"]
    for bare_col in bare_cols:
        for prefix in prefixes:
            cols.append(prefix + bare_col)

    if algo.name == "md4" or algo.name == "md5":
        cols.append("family")
        cols.append("input_family")
        cols.append("rounds")
        cols.append("min_round")
        cols.append("max_round")
    elif algo.name == "sha3":
        cols.append("rounds")
        cols.append("min_round")
        cols.append("max_round")
        cols.append("w")

    return cols

def create_table_query(algo, name=None, db_type="sqlite3"):
    if name == None:
        name = "c_" + algo.name
    cols = table_cols(algo)
    cols.append("tag")
    q = "CREATE TABLE " + name + " ("

    if db_type == "psql":
        q += "id BIGSERIAL, "

    for col in cols:
        q += col + " TEXT, "
    q = q[:-2] + ");"
    return q

def insert_query(table, d):
    q = "INSERT INTO " + table + " ("
    for k in d:
        q += k + ","
    q = q[:-1] + ") VALUES ("
    for k in d:
        q += "'" + d[k] + "',"
    q = q[:-1] + ");"
    return q

def build_deltas(db, algo, et):
    bare_cols = attacks_table_cols(algo)
    for bare_col in bare_cols:
        et["d" + bare_col] = models.vars.compute_ddelta(et["h1" + bare_col], et["h2" + bare_col])
        et["r" + bare_col] = models.vars.compute_rdelta(et["h1" + bare_col], et["h2" + bare_col])
    return et

def __insert__(db, table, values, commit=False, rowid=True):
    assert(type(table) == str)
    assert(type(values) == dict or (type(values) == list and len(values) > 0 and type(values[0]) == dict))
    rids = []
    if type(values) == dict:
        values = [values]
    for value in values:
        q = insert_query(table, value)
        result = db.execute(q, commit=False, rowid=rowid)
        if result != None and rowid:
            r, rid = result
            rids.append(rid)
    if commit:
        self.conn.commit()
    return rids

def insert_db_single(algo, db, col, commit=False, verify=True):
    if verify and not verify_collision(algo, col):
        return
    return __insert__(db, "c_" + algo.name, col, commit=False)

def import_db_multiple(algo, db, cols):
    for r in cols:
        et = {}
        for k in r:
            if r[k] != None:
                et[k] = r[k]
        __insert__(db, "c_" + algo.name, et, commit=False, rowid=False)
    db.commit()

def insert_db_multiple(algo, db, cols, tag, verify=True):
    for r in cols:
        h1 = unprefix_keys(r, "h1")
        h1 = algo.to_hex(h1)
        #print_dict(h1, "h1")

        h2 = unprefix_keys(r, "h2")
        h2 = algo.to_hex(h2)
        #print_dict(h2, "h2")

        h1s = b_hex_to_block(h1['state'])
        h1b = b_hex_to_block(h1['block'])
        h2s = b_hex_to_block(h2['state'])
        h2b = b_hex_to_block(h2['block'])

        import_single(algo, db, h1s, h1b, h2s, h2b, tag, commit=False)
    db.commit()


def insert_db_multiple_automatic_tag(algo, db, cols, verify=True):
    rids = []
    for r in cols:
        h1 = unprefix_keys(r, "h1")
        h1 = algo.to_hex(h1)
        #print_dict(h1, "h1")

        h2 = unprefix_keys(r, "h2")
        h2 = algo.to_hex(h2)
        #print_dict(h2, "h2")

        h1s = b_hex_to_block(h1['state'])
        h1b = b_hex_to_block(h1['block'])
        h2s = b_hex_to_block(h2['state'])
        h2b = b_hex_to_block(h2['block'])

        rid = import_single_automatic_tag(algo, db, h1s, h1b, h2s, h2b, commit=False)
        rids.extend(rid)
    db.commit()
    return rids

def build_col_row(algo, db, s1, b1, s2, b2, tag):
    et1 = algo.evaluate(b1, s1)
    et1 = algo.sanitize(et1)
    et1 = prefix_keys(et1, "h1")

    et2 = algo.evaluate(b2, s2)
    et2 = algo.sanitize(et2)
    et2 = prefix_keys(et2, "h2")

    jet = merge_dict([et1, et2])

    et = build_deltas(db, algo, jet)
    et['tag'] = tag

    return et


def build_col_row_automatic_tag(algo, db, s1, b1, s2, b2):
    et1 = algo.evaluate(b1, s1)
    et1 = algo.sanitize(et1)
    et1 = prefix_keys(et1, "h1")

    et2 = algo.evaluate(b2, s2)
    et2 = algo.sanitize(et2)
    et2 = prefix_keys(et2, "h2")

    jet = merge_dict([et1, et2])

    et = build_deltas(db, algo, jet)

    dplaces = loose_abs(algo, et)
    tag = algo.name + "-r" + str(algo.rounds) + "-e" + '-'.join(map(str, dplaces))

    et['tag'] = tag

    return et

def build_col_rows(algo, db, rs, tag):
    result = []
    for r in rs:
        h1 = unprefix_keys(r, "h1")
        h1 = algo.to_hex(h1)
        #print_dict(h1, "h1")

        h2 = unprefix_keys(r, "h2")
        h2 = algo.to_hex(h2)
        #print_dict(h2, "h2")

        h1s = b_hex_to_block(h1['state'])
        h1b = b_hex_to_block(h1['block'])
        h2s = b_hex_to_block(h2['state'])
        h2b = b_hex_to_block(h2['block'])

        et = build_col_row(algo, db, h1s, h1b, h2s, h2b, tag)
        result.append(et)
    return result

def import_single(algo, db, s1, b1, s2, b2, tag, commit=False):
    et = build_col_row(algo, db, s1, b1, s2, b2, tag)

    for i in range(0, algo.state_size//algo.int_size):
        if not et["h1o" + str(i)] == et["h2o" + str(i)]:
            if commit:
                db.commit()
            return

    __insert__(db, "c_" + algo.name, et)
    if commit:
        db.commit()


def import_single_automatic_tag(algo, db, s1, b1, s2, b2, commit=False):
    et = build_col_row_automatic_tag(algo, db, s1, b1, s2, b2)

    for i in range(0, algo.state_size//algo.int_size):
        if not et["h1o" + str(i)] == et["h2o" + str(i)]:
            if commit:
                db.commit()
            return None

    rids = __insert__(db, "c_" + algo.name, et)
    if commit:
        db.commit()
    return rids

def load_db_single(algo, db, id, name=None):
    if name is None:
        name = "c_" + algo.name
    cols = table_cols(algo)
    if not 'tag' in cols:
        cols.append("tag")
    r = db.query(name, cols, rowid=id, limit=1)
    return r

def load_db_tag(algo, db, tag, name=None):
    if name is None:
        name = "c_" + algo.name
    cols = table_cols(algo)
    if not 'tag' in cols:
        cols.append("tag")
    r = db.query(name, cols, tag=tag)
    return r

def load_db(algo, db, name=None):
    if name is None:
        name = "c_" + algo.name
    cols = table_cols(algo)
    if not 'tag' in cols:
        cols.append("tag")
    r = db.query(name, cols)
    return r

def verify_collision(algo, col):
    h1 = algo.to_hex(unprefix_keys(col, "h1"))
    h2 = algo.to_hex(unprefix_keys(col, "h2"))

    et1 = algo.evaluate(b_hex_to_block(h1['block']), b_hex_to_block(h1['state']))
    et1 = algo.sanitize(et1)
    et1 = prefix_keys(et1, "h1")

    et2 = algo.evaluate(b_hex_to_block(h2['block']), b_hex_to_block(h2['state']))
    et2 = algo.sanitize(et2)
    et2 = prefix_keys(et2, "h2")

    jet = merge_dict([et1, et2])

    for i in range(0, algo.state_size//algo.int_size):
        if jet["h1o" + str(i)] != jet["h2o" + str(i)] or jet['h1o' + str(i)] != col['h1o' + str(i)] or jet['h2o' + str(i)] != col['h2o' + str(i)]:
            return False

    for i in range(0, algo.rounds):
        if jet['h1i' + str(i)] != col['h1i' + str(i)] or jet['h2i' + str(i)] != col['h2i' + str(i)]:
            return False

    return True

def get_state(algo, eval_table, prefix):
    r = []
    for i in range(0, algo.state_size//algo.int_size):
        r.append(eval_table[prefix + "s" + str(i)])
    return ''.join(r)

def get_block(algo, eval_table, prefix):
    r = []
    for i in range(0, algo.block_size//algo.int_size):
        r.append(eval_table[prefix + "b" + str(i)])
    return ''.join(r)

def find_invalid(algo, db):
    r = ""
    v = "." *  algo.int_size
    q = "SELECT * FROM c_" + algo.name + " WHERE "
    c = []
    for i in range(0, algo.block_size//algo.int_size):
        c.append("db" + str(i) + "=='" + v + "'")
    q += " AND ".join(c)
    q += ";"
    print(q)
    #db.execute(q)
    db.commit()
