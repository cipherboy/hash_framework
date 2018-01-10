import hash_framework
import functools, random
from compute import cset


def __main__():
    pass

def _h(host, processes):
    r = []
    min_port = 5000
    for i in range(0, processes):
        r.append("http://" + host + ":" + str(min_port + i))
    return r

if __name__ == "__main__":
    print(len(cset))
    cs = hash_framework.manager.build_client_set(cset)

    kernel_name = "minimal"
    kernel = hash_framework.kernels.lookup(kernel_name)

    start_state = ""
    start_block = ""

    # Default start state
    # start_state = "FTTFFTTTFTFFFTFTFFTFFFTTFFFFFFFTTTTFTTTTTTFFTTFTTFTFTFTTTFFFTFFTTFFTTFFFTFTTTFTFTTFTTTFFTTTTTTTFFFFTFFFFFFTTFFTFFTFTFTFFFTTTFTTF"

    # Alexander Scheel
    # start_block = "FTTTTFFFFTTFFTFTFTTFTTFFFTFFFFFTFTTFFTFTFTTFFTFFFTTFTTTFFTTFFFFTFTTFFFTTFTFTFFTTFFTFFFFFFTTTFFTFFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFF"

    # Alexander Scheel <alexander.m.scheel@gmail.com>\n
    # start_block = "FTTTTFFFFTTFFTFTFTTFTTFFFTFFFFFTFTTFFTFTFTTFFTFFFTTFTTTFFTTFFFFTFTTFFFTTFTFTFFTTFFTFFFFFFTTTFFTFFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFFFTTFTTFFFTTFFFFTFFTTTTFFFFTFFFFFFTTFTTTFFTTFFFFTFTTTTFFFFTTFFTFTFFTFTTTFFTTTFFTFFTTFFTFTFTTFFTFFFTTFFFTTFTTTFFTTFFTFTTTFFTTFTTFTFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFFFTTFFFFTFTTFTTFTFTTFFTTTFTFFFFFFFTTFFFTTFFTFTTTFFTTFTTFFFTTFTFFTFFFFTFTFFFTTTTTFFTTFTTFTFTTFTTTT"

    # Full Second Preimage
    # start_block = "FTTTTFFFFTTFFTFTFTTFTTFFFTFFFFFTFTTFFTFTFTTFFTFFFTTFTTTFFTTFFFFTFTTFFFTTFTFTFFTTFFTFFFFFFTTTFFTFFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFFFTTFTTFFFTTFFFFTFFTTTTFFFFTFFFFFFTTFTTTFFTTFFFFTFTTTTFFFFTTFFTFTFFTFTTTFFTTTFFTFFTTFFTFTFTTFFTFFFTTFFFTTFTTTFFTTFFTFTTTFFTTFTTFTFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFFFTTFFFFTFTTFTTFTFTTFFTTTFTFFFFFFFTTFFFTTFFTFTTTFFTTFTTFFFTTFTFFTFFTFFFFFFFTTTTTFFTTFTTFTFTTFTTTTFTTFTTTTFTTFFFTTFTTFFTFTFTFTFFTTFTFTFFFFFFTFFFFFFTTFFTFFFTTFTTTFFTTFTTFTFTTFTFFTFTTFFTFTFTTTFFTFFFFFTFTFFTTFFTFTFTTFFTTTFTTFFFFT"
    # start_block = "T" * 512

    algo = hash_framework.algorithms.md4()
    db = hash_framework.database()

    work = kernel.gen_work([36], [2])

    # print(work)
    print(len(work))
    assert(False)

    # neighborhood
    tags = []
    work_mapped = list(map(lambda y: kernel.work_to_args("md4", y, start_state=start_state, start_block=start_block, ascii_block=False, both_ascii=False), work))

    on_result = functools.partial(kernel.on_result, algo, db)

    sat_list = set()
    rs = hash_framework.manager.run(cs, work_mapped, kernel_name, on_result)
    for rid in rs:
        r = rs[rid]
        if r != None and 'results' in r and len(r['results']) > 0:
            sat_list.add(work[rid])

    print(sat_list)
    db.commit()
