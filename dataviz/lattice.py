import sqlite3, json
import hash_framework as hf
import png

DOT = "/tmp/lattice.dot"


db = hash_framework.database()
query = "SELECT DISTINCT(tag) FROM c_md5;"
rs = db.execute(query)
results = []
for r in rs:
    results.append(r[0])

points = list(
    map(
        lambda y: tuple([y[0], tuple(y[1:])]),
        list(
            map(
                lambda x: list(
                    map(int, x.replace("e", "").replace("r", "").split("-")[1:])
                ),
                results,
            )
        )[:-2],
    )
)


w_graph = {}
for a in range(0, len(points)):
    p_a = points[a]
    w_graph[a] = set()
    r_a = p_a[0]
    s_a = set(p_a[1])
    for b in range(0, len(points)):
        if a == b:
            continue
        p_b = points[b]
        r_b = p_b[0]
        s_b = set(p_b[1])
        if r_a <= r_b and s_a.issubset(s_b):
            w_graph[a].add(b)

print(w_graph)


f = open(DOT, "w")
f.write("digraph dataviz {\n")
f.write('size="10,10";' + "\n")
f.write("overlap = false;\n")
f.write("splines = true;\n")
f.write(
    'node [\ncolor="#7C2529";\nfontcolor="#7C2529";\n];\nedge [\ncolor="#F1BE48";\n];\n'
)
f.write("\n\n")

for e in w_graph:
    f.write("v" + str(e) + ' [label="' + str(points[e]) + '"];\n')

f.write("\n\n")
for u in w_graph:
    for v in w_graph[u]:
        f.write("v" + str(u) + "->v" + str(v) + ";\n")


f.write("}\n")
f.flush()
f.close()
