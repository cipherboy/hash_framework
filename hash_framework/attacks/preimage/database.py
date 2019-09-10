from hash_framework.attacks.utils import table_cols as attacks_table_cols
from hash_framework.database import database
from hash_framework.models import models
from hash_framework.utils import *

import sqlite3


def create_table(algo, db):
    q = create_table_query(algo, db_type=db.type)
    db.execute(q, limit=1)


def table_cols(algo):
    cols = []
    bare_cols = attacks_table_cols(algo)
    for bare_col in bare_cols:
        cols.append("h" + bare_col)

    if algo.name == "md4" or algo.name == "md5":
        cols.append("family")
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
        name = algo.name
    cols = table_cols(algo)
    cols.append("tag")
    q = "CREATE TABLE " + name + " ("

    if db_type == "psql":
        q += "id BIGSERIAL, "

    for col in cols:
        q += col + " TEXT, "
    q = q[:-2] + ");"
    return q
