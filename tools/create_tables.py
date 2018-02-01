import hash_framework
import sys

def print_usage():
    print("Usage: ")
    print("\t" + sys.argv[0] + " --help")
    print("\t" + sys.argv[0] + " sqlite [/path/to/worker_results.db]")
    print("\t" + sys.argv[0] + " psql")

def __main__():
    db = hash_framework.database()

    if len(sys.argv) >= 2:
        if sys.argv[1] == 'sqlite' or sys.argv[1] == 'sqlite3':
            db_path = config.results_dir + "/worker_results.db"
            if len(sys.argv) == 3:
                db_path = sys.argv[2]

            db.close()
            db = hash_framework.database(path=db_path)
        elif sys.argv[1] == 'psql':
            db.close()
            db.init_psql()
        else:
            print_usage()
            return


    for name in hash_framework.algorithms.all_algorithms:
        algo = hash_framework.algorithms.lookup(name)

        try:
            hash_framework.attacks.collision.create_table(algo, db)
        except:
            pass

if __name__ == "__main__":
    __main__()
