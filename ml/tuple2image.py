#!/usr/bin/env python3

import hash_framework as hf
import json, png, sys

def write_tuple(rounds, places, run_return):
    out_name = "images/" + run_return + "-r" + str(rounds) + "-p" + '-'.join(map(str, places)) + ".png"

    #7C2529
    difference = (0xFF, 0x00, 0x00)
    no_difference = (0x00, 0x00, 0xFF)
    background_color = (0xFF, 0xFF, 0xFF)
    box_width = 1
    box_height = 1
    image_width = 16
    image_height = 3
    width = box_width*image_width
    height = box_height*image_height
    arr = []
    for i in range(0, height):
        na = []
        for j in range(0, width):
            na.append(background_color)
        arr.append(na)

    for i in range(0, rounds):
        bx = i % image_width
        by = i // image_width
        for x in range(box_width*bx, box_width*bx + box_width):
            for y in range(box_height*by, box_height*by + box_height):
                arr[y][x] = no_difference

    for i in places:
        bx = i % image_width
        by = i // image_width
        for x in range(box_width*bx, box_width*bx + box_width):
            for y in range(box_height*by, box_height*by + box_height):
                arr[y][x] = no_difference

    png.from_array(arr, 'RGB').save(out_name)


def __main__():
    db = hf.database()
    db.close()
    db.init_psql()

    assert(len(sys.argv) == 2)
    tid = int(sys.argv[1])

    q = "SELECT id, run_return, run_time, args FROM jobs WHERE task_id=" + str(tid) + " AND state=2 ORDER BY run_time DESC;"
    r, cur = db.execute(q, cursor=True)

    results = []

    row = cur.fetchone()
    while row != None:
        jid, run_return, run_time, args = row
        obj = json.loads(args)
        algo = obj['algo']
        rounds = obj['rounds']
        places = obj['places']

        if run_return == 10:
            write_tuple(rounds, places, 'sat')
        elif run_return == 20:
            write_tuple(rounds, places, 'unsat')

        row = cur.fetchone()



__main__()
