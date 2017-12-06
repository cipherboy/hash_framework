import sqlite3, json
import hash_framework as hf
import png

DOT="/tmp/lattice.dot"


points = [(8, (3,)),
(16, (3, 5, 7)),
(16, (3, 5, 7, 9)),
(20, (0, 3, 4, 5, 9, 11, 12)),
(20, (1, 3, 5, 7, 9, 10, 11, 12, 13)),
(20, (1, 3, 5, 7, 9, 10, 11, 12, 15)),
(48, (1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 19, 20, 35, 36)),
(48, (0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 15, 16, 20, 32))]


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


f = open(DOT, 'w')
f.write("digraph dataviz {\n")
f.write('size="10,10";' + "\n")
f.write("overlap = false;\n")
f.write("splines = true;\n")
f.write('node [\ncolor="#7C2529";\nfontcolor="#7C2529";\n];\nedge [\ncolor="#F1BE48";\n];\n')
f.write("\n\n")

for e in w_graph:
    f.write("v" + str(e) + " [label=\"" + str(points[e]) + "\"];\n")

f.write("\n\n")
for u in w_graph:
    for v in w_graph[u]:
        f.write("v" + str(u) + "->v" + str(v) + ";\n")


f.write("}\n")
f.flush()
f.close()
