from typing import List, Optional

import hash_framework.algorithms as hfa
import hash_framework.utils as hfu

def get_columns(db, algo, prefix: Optional[str] = None) -> List[str]:
    """
    Create the columns for a single instance of a hash function. This returns
    the initialization vector, the block, all the rounds, and the result.
    """
    algo = hfa.resolve(algo)
    cols = algo.columns()
    return hfu.prefix_list(cols, prefix)

def typed_cols(db, algo, columns, binary=False):
    algo = hfa.resolve(algo)
    result = []
    for column in columns:
        column_type = db.to_type(algo.type(column), binary=binary)
        result.append(f"{column} {column_type}")
    return result

def create_table_single(db, algo, table_name, prefix=None, additional=None):
    q = f"CREATE TABLE {table_name} ("
    cols = get_columns(db, algo, prefix)
    columns = typed_cols(db, algo, cols)
    if additional:
        columns.extend(additional)
    q += ", ".join(columns)
    q += ");"
    return q

def create_table_collision(db, algo, table_name, prefixes=['h1_', 'h2_'], additional=None):
    q = f"CREATE TABLE {table_name} ("
    columns = []
    for prefix in prefixes:
        cols = get_columns(db, algo, prefix)
        columns.extend(typed_cols(db, algo, cols))
    for prefix in ('xor_', 'sxor_'):
        cols = get_columns(db, algo, prefix)
        columns.extend(typed_cols(db, algo, cols, binary=True))
    if additional:
        columns.extend(additional)
    q += ", ".join(columns)
    q += ");"
    return q
