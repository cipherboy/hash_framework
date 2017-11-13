import time
from hash_framework.manager.client import Client
from multiprocessing.pool import ThreadPool
import hash_framework.kernels

def build_client_set(uris):
    if type(uris) == str:
        uris = [uris]

    cs = []
    for uri in uris:
        cs.append(Client(uri))

    return cs

def _send_sats(client_list, work_list, kernel_name):
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

    return jids, work_map


def run(client_list, work_list, kernel_name):
    jids, work_map = _send_sats(client_list, work_list, kernel_name)

    def _read_job(jid):
        csi = work_map[jid][0]
        wid = work_map[jid][1]
        c = client_list[csi]
        if c.finished(jid):
            d = c.result(jid)
            return (jid, wid, d)
        return None

    pool = ThreadPool(processes=4)
    results = {}
    while True:
        res = pool.map(_read_job, jids)
        for r in res:
            if r == None:
                continue
            jid, wid, d = r
            jids.remove(jid)
            results[wid] = d
        if len(jids) == 0:
            break
        time.sleep(0.5)
    return results
