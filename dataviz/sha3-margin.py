import png
import os

all_results = []
for w in [4, 8]:
    bp = "/home/cipherboy/GitHub/hash_framework/results/sha3/"
    for i in range(0, 25 * w + 2):
        try:
            e = eval(
                open(
                    "/home/cipherboy/GitHub/hash_framework/results/sha3/results-"
                    + str(w)
                    + "-"
                    + str(i)
                    + ".json",
                    "r",
                ).read()
            )
            if type(e) == list:
                all_results += e
        except Exception as e:
            print(str(e) + " -- " + str(w) + "-" + str(i))
            pass

results = {}
for e in all_results:
    w = e[0]
    i = e[1]
    if not w in results:
        results[w] = {}

    if not i in results[w]:
        results[w][i] = set()

    results[w][i].add(e)

print(len(all_results))


def draw_table(results, size, out_name="/tmp/table.png"):
    # 7C2529
    sat_color = (0xF1, 0xBE, 0x48)
    unsat_color = (0x7C, 0x25, 0x29)
    error_color = (0xFF, 0x00, 0x00)
    background_color = (0xFF, 0xFF, 0xFF)
    box_width = 8
    box_height = 8
    width = box_width * size
    height = box_height * size
    arr = []
    for i in range(0, height):
        na = []
        for j in range(0, width):
            na.append(background_color)
        arr.append(na)
    for r in results:
        in_m = r[2]
        out_m = r[3]
        color = r[4]
        for x in range(box_width * in_m, box_width * in_m + box_width):
            if color:
                for y in range(box_height, box_height * out_m + box_height):
                    if arr[y][x] == background_color:
                        arr[y][x] = sat_color
            else:
                for y in range(box_height * out_m, height):
                    if arr[y][x] == background_color:
                        arr[y][x] = unsat_color
    png.from_array(arr, "RGB").save(out_name)


for w in results:
    for i in results[w]:
        draw_table(
            list(results[w][i]),
            25 * w + 2,
            "/tmp/sha3-w" + str(w) + "-i" + str(i) + ".png",
        )
