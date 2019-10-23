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

def create_table_single(db, algo, name):
    cols = get_columns(db, algo)
    q = f"CREATE TABLE {name} ("
    ",".join(typed_cols(db, cols))
    q += ");"
