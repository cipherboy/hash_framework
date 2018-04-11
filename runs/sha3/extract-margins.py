#!/usr/bin/env python3

import hash_framework as hf
import json, png, sys


def draw_table(results, size, out_name="/tmp/table.png"):
    #7C2529
    sat_color = (0xF1, 0xBE, 0x48)
    unsat_color = (0x7C, 0x25, 0x29)
    error_color = (0xFF, 0x00, 0x00)
    background_color = (0xFF, 0xFF, 0xFF)
    box_width = 8
    box_height = 8
    width = box_width*size
    height = box_height*size
    arr = []
    for i in range(0, height):
        na = []
        for j in range(0, width):
            na.append(background_color)
        arr.append(na)
    for i in range(0, size):
        for j in range(0, size):
            if results[i][j] == 0:
                continue

            color = error_color
            if results[i][j] == 10:
                color = sat_color
            elif results[i][j] == 20:
                color = unsat_color

            for x in range(box_width*i, box_width*i + box_width):
                for y in range(box_height*j, box_height*j + box_height):
                    arr[y][x] = color
    png.from_array(arr, 'RGB').save(out_name)

def __main__():
    db = hf.database()
    db.close()
    db.init_psql()

    assert(len(sys.argv) == 3)
    tid = int(sys.argv[1])

    q = "SELECT id, run_return, args FROM jobs WHERE task_id=" + str(tid) + " AND state=2;"
    r, cur = db.execute(q, cursor=True)

    results = {}
    for i in [1, 2, 3, 4, 5, 6, 7, 8]:
        results[i] = {}
        for w in [1, 2, 4, 8, 16]:
            arr = []
            for j in range(0, 25*w):
                arr.append([0] * (25*w))
            results[i][w] = arr

    row = cur.fetchone()
    while row != None:
        jid, run_result, args = row
        obj = json.loads(args)
        w = obj['w']
        input_error = obj['input_error']
        input_margin = obj['input_margin']
        output_margin = obj['output_margin']
        if input_error in results and w in results[input_error]:
            results[input_error][w][input_margin][output_margin] = run_result
        else:
            print((w, input_error))

        row = cur.fetchone()

    for i in results:
        for w in results[i]:
            draw_table(results[i][w], 25*w, "/tmp/table-margins-" + sys.argv[2] + "-w" + str(w) + "-i" + str(i) + "-o0.png")


__main__()
