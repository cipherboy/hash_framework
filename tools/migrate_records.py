import hash_framework
import sys

def __main__():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " algorithm /path/to/results.db")
        return

    db = hash_framework.database()
    db.close()
    db.init_psql()

    algo = hash_framework.algorithms.lookup(sys.argv[1])()
    hash_framework.attacks.collision.import_from_other(db, algo, sys.argv[2])

if __name__ == "__main__":
    __main__()
