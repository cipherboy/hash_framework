import hash_framework
from compute import cset
import functools


def __main__():
    print(len(cset))
    cs = hash_framework.manager.build_client_set(cset)

    kernel_name = "families"
    kernel = hash_framework.kernels.lookup(kernel_name)
    algo = hash_framework.algorithms.md4()
    db = hash_framework.database()

    c_jids = []
    for c in cs:
        c_jids.append(c.all_jobs())

    on_result = functools.partial(kernel.on_result, algo, db)
    hash_framework.manager.core.wait_results(cs, c_jids, on_result)


if __name__ == "__main__":
    __main__()
