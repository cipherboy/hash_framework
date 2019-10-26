import hash_framework.algorithms as hfa
import hash_framework.database as hfd
import hash_framework.utils as hfu

def test_get_columns():
    with hfu.tmp_dir() as tdir:
        print(tdir)
        db = hfd.Database(f"{tdir}/database.db")
        algo = hfa.md4()
        assert hfd.get_columns(db, algo)

        prefixed = hfd.get_columns(db, algo, "something")
        for item in prefixed:
            assert item.startswith("something")
