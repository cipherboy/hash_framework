import png

data = [(8, 2, 20), (8, 4, 20), (6, 16, 10), (6, 32, 10), (6, 64, 10), (7, 1, 10), (7, 2, 10), (7, 4, 10), (7, 8, 10), (7, 16, 10), (7, 32, 10), (7, 64, 10), (8, 1, 20), (8, 8, 20), (6, 4, 10), (6, 8, 10), (5, 1, 10), (5, 2, 10), (5, 4, 10), (5, 8, 10), (5, 16, 10), (6, 1, 10), (5, 32, 10), (6, 2, 10), (5, 64, 10), (8, 16, 20), (8, 32, 20), (8, 64, 20), (9, 1, 10), (9, 2, 10), (9, 4, 10), (9, 8, 10), (9, 16, 10), (9, 32, 10), (9, 64, 10), (10, 1, 10), (10, 2, 10), (10, 4, 10), (10, 8, 10), (10, 16, 10), (10, 32, 10), (10, 64, 10), (11, 1, 10), (11, 2, 10), (11, 4, 10), (11, 8, 10), (11, 16, 10), (11, 32, 10), (11, 64, 10), (12, 1, 20), (12, 2, 20), (12, 4, 20), (12, 8, 20), (12, 16, 20), (12, 32, 20), (12, 64, 20), (13, 1, 10), (13, 2, 10), (13, 4, 10), (13, 8, 10), (13, 16, 10), (13, 32, 10), (13, 64, 10), (14, 1, 10), (14, 2, 10), (14, 4, 10), (14, 8, 10), (14, 16, 10), (14, 32, 10), (14, 64, 10), (15, 1, 10), (15, 2, 10), (15, 4, 10), (15, 8, 10), (15, 16, 10), (15, 32, 10), (15, 64, 10), (16, 1, 20), (16, 2, 20), (16, 4, 20), (16, 8, 20), (16, 16, 20), (16, 32, 20), (16, 64, 20), (17, 1, 10), (17, 2, 10), (17, 4, 10), (17, 8, 10), (17, 16, 10), (17, 32, 10), (17, 64, 10), (18, 1, 10), (18, 2, 10), (18, 4, 10), (18, 8, 10), (18, 16, 10), (18, 32, 10), (18, 64, 10), (19, 1, 10), (19, 2, 10), (19, 4, 10), (19, 8, 10), (19, 16, 10), (19, 32, 10), (19, 64, 10), (20, 1, 20), (20, 2, 20), (20, 4, 20), (20, 8, 20), (20, 16, 20)]


sdata = {}
for r in range(1, 25):
    sdata[r] = {}
    for w in [1, 2, 4, 8, 16, 32, 64]:
        sdata[r][w] = 0

for d in data:
    sdata[d[0]][d[1]] = d[2]

matrix = []
for i in range(1, 25):
    matrix.append([0] * 7)

for i_pos in range(0, 24):
    i = i_pos + 1
    for j_pos in range(0, 7):
        w = 1 << j_pos
        matrix[i_pos][j_pos] = sdata[i][w]


def draw_table(results, w, h, out_name="/tmp/table.png"):
    #7C2529
    sat_color = (0xF1, 0xBE, 0x48)
    unsat_color = (0x7C, 0x25, 0x29)
    error_color = (0xFF, 0x00, 0x00)
    background_color = (0xFF, 0xFF, 0xFF)
    box_width = 8
    box_height = 8
    width = box_width*w
    height = box_height*h
    arr = []
    for i in range(0, height):
        na = []
        for j in range(0, width):
            na.append(background_color)
        arr.append(na)
    for i in range(0, w):
        for j in range(0, h):
            if results[j][i] == 0:
                continue

            color = error_color
            if results[j][i] == 10:
                color = sat_color
            elif results[j][i] == 20:
                color = unsat_color

            for x in range(box_width*i, box_width*i + box_width):
                for y in range(box_height*j, box_height*j + box_height):
                    arr[y][x] = color
    png.from_array(arr, 'RGB').save(out_name)

print(matrix)
draw_table(matrix, 7, 24, out_name="/tmp/table-distributivity-c.png")
