#!/usr/bin/env python3

import hash_framework as hf

def tc_create_task():
    db = hf.database()
    db.close()
    db.init_psql()

    t = hf.manager.Task(db)
    t.new("test-md4-test", "md4", 10, 10000)
    assert(t.id != None)

    return True

def tc_load_task():
    db = hf.database()
    db.close()
    db.init_psql()

    t = hf.manager.Task(db)
    t.load("test-md4-test")
    assert(t.name == "test-md4-test")
    assert(t.algo == "md4")
    assert(t.max_threads == 10)
    assert(t.priority == 10000)

    return True

def tc_delete_task():
    db = hf.database()
    db.close()
    db.init_psql()

    t = hf.manager.Task(db)
    t.load("test-md4-test").remove()

    return True


def __main__():
    tests = [tc_create_task, tc_load_task, tc_delete_task]

    for test in tests:
        ret = test()
        if ret:
            print(test.__name__ + "... OK")
        else:
            print(test.__name__ + "... Failed")
            break

if __name__ == "__main__":
    __main__()
