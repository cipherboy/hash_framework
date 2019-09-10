import hash_framework.attacks as attacks


class visualizations:
    def render_graph(graph, names, filename):
        print("Start render_graph")
        f = open(filename, 'w')
        f.write("graph rendered {\n")
        for e in names:
            f.write('v' + str(e) + ' [label="' + names[e] + '"];' + "\n")

        for v in graph:
            for u in graph[v]:
                if u <= v:
                    f.write('v' + str(u) + " -- v" + str(v) + ";\n")

        f.write("}\n")
        f.flush()
        f.close()
        print("End render_graph")

    def unit_step_graph(algo, cols):
        graph = {}
        names = {}
        print("Start unit_step_graph")
        for i in range(0, len(cols)):
            graph[i] = set()
        for i in range(0, len(cols)):
            for j in range(i+1, len(cols)):
                if attacks.collision.metric.loose.distance(algo, cols[i], cols[j]) == 1:
                    graph[i].add(j)
                    graph[j].add(i)
        for i in range(0, len(cols)):
            if 'ROWID' in cols[i]:
                names[i] = cols[i]['ROWID']
            else:
                print(str(list(cols[i].keys())))
        print("End unit_step_graph")
        return graph, names
