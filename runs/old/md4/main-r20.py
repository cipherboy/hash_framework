import hash_framework
import functools, random


def __main__():
    pass


def build_clause(
    block="FTTTTFFFFTTFFTFTFTTFTTFFFTFFFFFTFTTFFTFTFTTFFTFFFTTFTTTFFTTFFFFTFTTFFFTTFTFTFFTTFFTFFFFFFTTTFFTFFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFFFTTFTTFFFTTFFFFTFFTTTTFFFFTFFFFFFTTFTTTFFTTFFFFTFTTTTFFFFTTFFTFTFFTFTTTFFTTTFFTFFTTFFTFTFTTFFTFFFTTFFFTTFTTTFFTTFFTFTTTFFTTFTTFTFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFFFTTFFFFTFTTFTTFTFTTFFTTTFTFFFFFFFTTFFFTTFFTFTTTFFTTFTTFFFTTFTFFTFFTFFFFFFFTTTTTFFTTFTTFTFTTFTTTTFTTFTTTTFTTFFFTTFTTFFTFTFTFTFFTTFTFTFFFFFFTFFFFFFTTFFTFFFTTFTTTFFTTFTTFTFTTFTFFTFTTFFTFTFTTTFFTFFFFFTFTFFTTFFTFTFTTFFTTTFTTFFFFT"
):
    clauses = []
    for i in range(0, len(block) // 32):
        clauses.append("h1b" + str(i) + '="' + block[i * 32 : (i + 1) * 32] + '"')
    return " AND " + (" AND ".join(clauses)) + " "


def from_tags(db):
    r = 32
    tags = db.execute(
        "SELECT DISTINCT tag FROM c_md4 WHERE tag LIKE '%r" + str(r + 4) + "%';"
    ).fetchall()
    print(len(tags))
    return list(
        map(
            lambda x: (r, tuple(map(int, x[9:].split("-")))),
            map(lambda y: "".join(y), tags),
        )
    )


def tag_neighbors(db):
    r = 20
    q = "SELECT DISTINCT tag FROM c_md4 WHERE tag LIKE '%r" + str(r) + "%' AND ROWID;"
    print(q)
    tags = db.execute(q).fetchall()
    print(len(tags))
    lt = list(
        map(
            lambda x: tuple(map(int, x[9:].split("-"))), map(lambda y: "".join(y), tags)
        )
    )
    lts = set(lt)
    ne = set()
    for delta in lt:
        for n in range(0, 3):
            for e in hash_framework.attacks.second.generate_test_delta(delta, n, r - 4):
                if e not in lts:
                    ne.add(e)
    print(len(lt))
    print(len(ne))
    return list(map(lambda x: (r, x), ne))


def tag_fill_in(db):
    r = 20
    tags = db.execute(
        "SELECT DISTINCT tag FROM c_md4 WHERE tag LIKE '%r" + str(r) + "%';"
    ).fetchall()
    print(len(tags))
    lt = list(
        map(
            lambda x: tuple(map(int, x[9:].split("-"))), map(lambda y: "".join(y), tags)
        )
    )
    ne = set()
    for delta in lt:
        for n in range(0, 5):
            for e in hash_framework.attacks.second.generate_reduced_test_delta(
                delta, n
            ):
                ne.add(e)

    for delta in lt:
        if delta in ne:
            ne.remove(delta)

    print(len(lt))
    print(len(ne))
    return list(map(lambda x: (r, x), ne))


def tag_neighborhood_extend(db, kernel):
    r = 44
    c = []
    for i in range(0, r):
        c.append("ri" + str(i))

    # 92411
    q = (
        "SELECT DISTINCT "
        + ",".join(c)
        + " FROM c_md4 WHERE tag LIKE '%r"
        + str(r)
        + "%' AND ROWID > 91811;"
    )
    # q = "SELECT DISTINCT " + ','.join(c) + " FROM c_md4 WHERE tag LIKE '%r" + str(r) + "%' AND ROWID = 91811;"
    print(q)
    bases = db.execute(q).fetchall()
    work = kernel.gen_work(r + 4, bases, [0, 1])
    random.shuffle(work)
    return work


def _h(host, processes):
    r = []
    min_port = 5000
    for i in range(0, processes):
        r.append("http://" + host + ":" + str(min_port + i))
    return r


if __name__ == "__main__":
    compute = _h("10.1.30.0", 4)
    compute += _h("10.1.30.1", 8)
    compute += _h("10.1.30.2", 8)
    compute += _h("10.1.30.3", 8)
    compute += _h("10.1.30.4", 8)
    compute += _h("10.1.30.5", 4)
    compute += _h("10.1.30.7", 4)
    compute += _h("10.1.30.9", 4)
    compute += _h("10.1.30.10", 4)
    moselle = _h("10.24.47.166", 16)
    cluster = _h("10.0.30.1", 8)
    cluster += _h("10.0.30.2", 8)
    cluster += _h("10.0.30.3", 8)
    cluster += _h("10.0.30.4", 8)
    cluster += _h("10.0.30.5", 8)
    cluster += _h("10.0.30.6", 8)
    cluster += _h("10.0.30.7", 8)
    cluster += _h("10.0.30.8", 8)
    cluster += _h("10.0.30.9", 8)
    cluster += _h("10.0.30.10", 8)
    cluster += _h("10.0.30.11", 8)
    cluster += _h("10.0.30.12", 8)
    playground = _h("10.1.30.101", 8)
    playground += _h("10.1.30.102", 8)
    playground += _h("10.1.30.103", 8)
    playground += _h("10.1.30.104", 8)
    playground += _h("10.1.30.105", 8)
    playground += _h("10.1.30.106", 8)
    playground += _h("10.1.30.107", 8)
    localhost = _h("127.0.0.1", 2)
    # cset = localhost
    cset = compute + playground + cluster
    cs = hash_framework.manager.build_client_set(cset)

    kernel_name = "second_preimage"
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

    # work = kernel.gen_work([20], list(range(0, 16)))
    work = tag_fill_in(db)
    wangs_base = [
        "................................",
        ".........................*......",
        ".....................*..*.......",
        "......*.........................",
        "................................",
        "..................*.............",
        "..........****..................",
        ".................***............",
        "...............*................",
        "......*..****...................",
        "..*.............................",
        "*...............................",
        "......*..*......................",
        "..**.*..........................",
        "................................",
        ".............*..................",
        "*..*.**.........................",
        "................................",
        "................................",
        "*.*.............................",
        "*.**............................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "*...............................",
        "*...............................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
    ]
    sasakis_base = [
        "*.............................**",
        "......................*.*.......",
        "....................*...........",
        "..........***...................",
        ".......***............*******...",
        "*..........***..................",
        "*......***............*********.",
        "................................",
        "......*.**......................",
        "***.***............*............",
        "...................*............",
        "...................*............",
        "..**..*.........................",
        "................................",
        "................................",
        "*...............................",
        "...*............................",
        "................................",
        "................................",
        "................................",
        "*...............................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "*...............................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
    ]
    kasselman_base = [
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "********************************",
        "................................",
        "...*...............*............",
        "...................*...........*",
        "................................",
        "................................",
        "..........................*.....",
        "......*.........................",
        "................................",
        "................................",
        ".................*..............",
        ".........................*......",
        "................................",
        "................................",
        "........*.......................",
        "............*...................",
        "................................",
        "................................",
        "...............................*",
        "...............................*",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
    ]
    dobbertins_base = [
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "********************************",
        "................................",
        "...*...............*............",
        "...................*...........*",
        "................................",
        "................................",
        "..........................*.....",
        "......*.........................",
        "................................",
        "................................",
        ".................*..............",
        ".........................*......",
        "................................",
        "............*...................",
        "........*.......................",
        "............*...................",
        "................................",
        "................................",
        "...............................*",
        "...............................*",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
    ]
    schlaffers_base = [
        "................................",
        ".........................*......",
        ".....................*..*.......",
        "......*.........................",
        "................................",
        "...............****.............",
        "........***..*..................",
        "...................*.*..........",
        ".....**.....*...................",
        "........****....................",
        "..*.............................",
        "*.*............................*",
        "..**..*..*.**...................",
        "................................",
        "................................",
        "............**.*................",
        "*..*..*.........................",
        "................................",
        "................................",
        "*...............................",
        "*..*............................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "*...............................",
        "*...............................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
    ]

    # Neighborhood
    # work = kernel.gen_work(48, [wangs_base, sasakis_base, kasselman_base, dobbertins_base, schlaffers_base], [0, 1, 2, 3])
    # work = tag_neighborhood_extend(db, kernel)

    # Zeroes / Ones
    # work = kernel.gen_work(48, [sasakis_base, kasselman_base, dobbertins_base, schlaffers_base])

    # Second Preimage
    # work = kernel.gen_work([32], [4, 5, 6])
    # work = tag_fill_in(db)
    # random.shuffle(work)
    # work = work[:100000]

    # work = [(32, (0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15)), (32, (0, 1, 2, 3, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15)), (32, (0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)), (32, (0, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), (32, (0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15)), (32, (0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15)), (32, (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15)), (32, (1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15)), (32, (0, 1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15)), (32, (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15)), (32, (0, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15)), (32, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), (32, (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15)), (32, (0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15)), (32, (0, 1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15)), (32, (0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), (32, (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15)), (32, (0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), (32, (0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 15)), (32, (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15)), (32, (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15)), (32, (0, 1, 2, 3, 4, 6, 7, 9, 10, 11, 12, 13, 14, 15)), (32, (0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15)), (32, (0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), (32, (0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15)), (32, (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15)), (32, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15))]
    # work = get_work()

    # work = [
    #    (40, (1, 2, 3, 35, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 19, 20, 36)),
    #    (44, (1, 2, 3, 35, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 19, 20, 36)),
    #    (40, (0, 1, 2, 3, 4, 5, 6, 32, 8, 9, 10, 11, 12, 15, 16, 20)),
    #    (44, (0, 1, 2, 3, 4, 5, 6, 32, 8, 9, 10, 11, 12, 15, 16, 20)),
    #    (40, (12, 14, 15, 18, 19, 22, 23, 26, 27, 30, 31)),
    #    (44, (12, 14, 15, 18, 19, 22, 23, 26, 27, 30, 31)),
    #    (40, (12, 14, 15, 18, 19, 22, 23, 25, 26, 27, 30, 31)),
    #    (44, (12, 14, 15, 18, 19, 22, 23, 25, 26, 27, 30, 31)),
    #    (40, (1, 2, 3, 35, 5, 6, 7, 8, 9, 10, 11, 12, 36, 15, 16, 19, 20)),
    #    (44, (1, 2, 3, 35, 5, 6, 7, 8, 9, 10, 11, 12, 36, 15, 16, 19, 20))
    # ]

    # print(work)
    print(len(work))
    # assert(False)

    # neighborhood
    tags = []
    # work_mapped = list(map(lambda y: kernel.work_to_args("md4", y, start_state=start_state, start_block=start_block, ascii_block=False, both_ascii=False), work))

    # second preimage
    work_mapped = list(
        map(lambda y: kernel.work_to_args("md4", start_state, start_block, y), work)
    )

    tags = list(map(lambda y: kernel.work_to_tag("md4", y), work))

    on_result = functools.partial(kernel.on_result, algo, db, tags, work)

    sat_list = set()
    rs = hash_framework.manager.run(cs, work_mapped, kernel_name, on_result)
    for rid in rs:
        r = rs[rid]
        if r != None and "results" in r and len(r["results"]) > 0:
            sat_list.add(work[rid])

    print(sat_list)
    db.commit()
