import time
import functools
from hash_framework.manager.client import Client
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool
import hash_framework.kernels


def build_client_set(uris):
    if type(uris) == str:
        uris = [uris]

    cs = []
    for uri in uris:
        cs.append(Client(uri))

    return cs


def _add_sats_client(arg):
    c_uri, post_data = arg
    c = Client(c_uri)
    return c.add_sats(post_data)


def _send_sats(client_list, work_list, kernel_name):
    csi = 0

    c_work = []
    c_post_data = []
    for i in range(len(client_list)):
        c_work.append([])
        c_post_data.append((client_list[i].uri, []))

    for wid in range(len(work_list)):
        post_data = {"kernel_name": kernel_name, "kernel_args": work_list[wid]}
        c_work[csi].append(wid)
        c_post_data[csi][1].append(post_data)
        csi = (csi + 1) % len(client_list)

    pool = Pool(processes=len(client_list))
    res_pool = pool.map(_add_sats_client, c_post_data)

    c_jids = []
    for i in range(len(client_list)):
        c_jids.append(res_pool[i])

    return c_jids


def wait_results(client_list, c_jids, on_results):
    results = {}
    except_count = 0

    while True:
        min_sleep = 0.5
        all_finished = True
        for i in range(len(client_list)):
            c = client_list[i]
            if len(c_jids[i]) == 0:
                continue

            all_finished = False

            # try:
            j_results = c.bulk_result(c_jids[i])
            if len(j_results) == 0:
                print("Received no results from " + c.uri)

            finished_jids = set()
            if len(j_results) > 0:
                print("Received results from " + c.uri + ": " + str(len(j_results)))

            for k in j_results:
                c_jids[i].remove(k)
                if on_results != None:
                    on_results(j_results[k])
                finished_jids.add(k)

            c.bulk_delete(list(finished_jids))

            if len(c_jids[i]) == 0:
                print("Client finished: " + c.uri)
                continue

            if len(c_jids[i]) > 10:
                min_sleep = 10

        if all_finished:
            break

        print(min_sleep)
        print(list(map(len, c_jids)))
        time.sleep(min_sleep)


def run(client_list, work_list, kernel_name, on_results=None):
    print("Sending sats...")
    c_jids = _send_sats(client_list, work_list, kernel_name)
    print("Waiting for results...")
    wait_results(client_list, c_jids, on_results)
