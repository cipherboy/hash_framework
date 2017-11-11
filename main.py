import hash_framework

def __main__():
    pass

if __name__ == "__main__":
    cset = []
    for i in range(0,11):
        cset.append("http://10.1.30." + str(i) + ":5000")
    cs = hash_framework.manager.build_client_set(cset)
    kernel_name = "second_preimage"
    kernel = hash_framework.kernels.lookup(kernel_name)
    start_state = "FTTFFTTTFTFFFTFTFFTFFFTTFFFFFFFTTTTFTTTTTTFFTTFTTFTFTFTTTFFFTFFTTFFTTFFFTFTTTFTFTTFTTTFFTTTTTTTFFFFTFFFFFFTTFFTFFTFTFTFFFTTTFTTF"
    start_block = "FTTTTFFFFTTFFTFTFTTFTTFFFTFFFFFTFTTFFTFTFTTFFTFFFTTFTTTFFTTFFFFTFTTFFFTTFTFTFFTTFFTFFFFFFTTTFFTFFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFFFTTFTTFFFTTFFFFTFFTTTTFFFFTFFFFFFTTFTTTFFTTFFFFTFTTTTFFFFTTFFTFTFFTFTTTFFTTTFFTFFTTFFTFTFTTFFTFFFTTFFFTTFTTTFFTTFFTFTTTFFTTFTTFTFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFFFTTFFFFTFTTFTTFTFTTFFTTTFTFFFFFFFTTFFFTTFFTFTTTFFTTFTTFFFTTFTFFTFFTFFFFFFFTTTTTFFTTFTTFTFTTFTTTTFTTFTTTTFTTFFFTTFTTFFTFTFTFTFFTTFTFTFFFFFFTFFFFFFTTFFTFFFTTFTTTFFTTFTTFTFTTFTFFTFTTFFTFTFTTTFFTFFFFFTFTFFTTFFTFTFTTFFTTTFTTFFFFT"
    work = kernel.gen_work([16], [1, 2, 3, 4])
    work_mapped = list(map(lambda y: kernel.work_to_args("md4", start_state, start_block, y), work))

    sat_list = set()
    rs = hash_framework.manager.run(cs, work_mapped, kernel_name)
    for rid in range(len(rs)):
        r = rs[rid]
        if r != None and len(r['results']) > 0:
            sat_list.add(work[rid])

    print(sat_list)
