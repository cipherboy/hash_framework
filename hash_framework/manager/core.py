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


    wzip = []
    for wid in range(len(work_list)):
        wzip.append((wid, csi))
        csi = (csi + 1) % len(client_list)

    def _add_sat(data):
        wid, csi = data
        work = work_list[wid]
        c = client_list[csi]
        jid = c.add_sat(kernel_name, work)
        if jid != False:
            return (jid, csi, wid)
        return None

    pool = ThreadPool(processes=len(client_list)*2)
    res = pool.map(_add_sat, wzip)

    work_map = {}
    jids = set()
    for r in res:
        if r == None:
            continue
        jid, csi, wid = r
        jids.add(jid)
        work_map[jid] = (csi, wid)

    return jids, work_map


def run(client_list, work_list, kernel_name):
    print("Sending sats...")
    jids, work_map = _send_sats(client_list, work_list, kernel_name)

    def _read_job(jid):
        csi = work_map[jid][0]
        wid = work_map[jid][1]
        c = client_list[csi]
        try:
            if c.finished(jid):
                d = c.result(jid)
                try:
                    c.delete(jid)
                except:
                    return None
                return (jid, wid, d)
        except:
            return None
        return None

    print("Waiting for sats to complete...")
    pool = ThreadPool(processes=len(client_list)*2)
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
        if len(jids) > 10:
            time.sleep(1)
        else:
            time.sleep(0.25)
    return results
