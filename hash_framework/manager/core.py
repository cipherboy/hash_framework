import time
from hash_framework.manager.client import Client
import hash_framework.kernels

def build_client_set(uris):
    if type(uris) == str:
        uris = [uris]

    cs = []
    for uri in uris:
        cs.append(Client(uri))

    return cs

def run(client_list, work_list, kernel_name):
    csi = 0

    jids = set()
    work_map = {}
    for wid in range(len(work_list)):
        work = work_list[wid]
        c = client_list[csi]
        jid = c.add_sat(kernel_name, work)
        if jid != False:
            jids.add(jid)
            work_map[jid] = (csi, wid)
            csi = (csi + 1) % len(client_list)

    results = [None] * len(work_list)
    while True:
        for jid in jids.copy():
            csi = work_map[jid][0]
            wid = work_map[jid][1]
            c = client_list[csi]
            if c.finished(jid):
                jids.remove(jid)
                d = c.result(jid)
                c.delete(jid)
                results[wid] = d
        if len(jids) == 0:
            break
        time.sleep(0.5)
    return results
