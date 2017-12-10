import hash_framework
import sys

def __main__():
    db = hash_framework.database()
    algo = hash_framework.algorithms.lookup(sys.argv[1])()
    hash_framework.attacks.collision.import_from_other(db, algo, sys.argv[2])

if __name__ == "__main__":
    __main__()
