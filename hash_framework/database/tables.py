import hash_framework.algorithms as hfa
import hash_framework.utils as hfu


def create_columns(db, algo, prefix: str = None):
    """
    Create the columns for a single instance of a hash function. This returns
    the initialization vector, the block, all the rounds, and the result.
    """
    algo = hfa.resolve(algo)
    return algo.columns()
