#!/usr/bin/python3

import hash_framework
import sys


def print_usage():
    print("Usage: ")
    print("\t" + sys.argv[0] + " --help")
    print("\t" + sys.argv[0] + " sqlite [/path/to/worker_results.db]")
    print("\t" + sys.argv[0] + " psql")


def __main__():
    db = hash_framework.database.Database()
    config = hash_framework.Config()

    if len(sys.argv) >= 2:
        if sys.argv[1] == "sqlite" or sys.argv[1] == "sqlite3":
            db_path = config.results_dir + "/framework_results.db"
            if len(sys.argv) == 3:
                db_path = sys.argv[2]

            db.close()
            db = hash_framework.database.Database(path=db_path)
        elif sys.argv[1] == "psql":
            db.close()
            db.init_psql()
        else:
            print_usage()
            return

    for name in ['md4', 'md5', 'sha1']:
        try:
            algo = hash_framework.algorithms.resolve(name)
            additional = []
            additional.append("tag TEXT")
            additional.append("generated TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            additional.append("rounds INTEGER")
            query = hash_framework.database.tables.create_table_collision(db, algo, f"{name}_collision", additional=additional)
            db.execute(query)
        except Exception as e:
            print(e, file=sys.stderr)


if __name__ == "__main__":
    __main__()
