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

def _add_sat(c, kernel_name, work_element):
    wid, work = work_element
    try:
        jid = c.add_sat(kernel_name, work)
        if jid != False:
            return (jid, wid)
    except Exception as e:
        print(e)
        return None
    return None

def _add_sat_client(datas):
    curi, kernel_name, works = datas
    c = Client(curi)
    cpool = ThreadPool(processes=2)
    res = cpool.map(functools.partial(_add_sat, c, kernel_name), works)
    return res


def _send_sats(client_list, work_list, kernel_name):
    csi = 0

    cwork = []
    for i in range(len(client_list)):
        cwork.append((client_list[i].uri, kernel_name, []))

    for wid in range(len(work_list)):
        cwork[csi][2].append((wid, work_list[wid]))
        csi = (csi + 1) % len(client_list)

    pool = Pool(processes=len(client_list))
    res_pool = pool.map(_add_sat_client, cwork)

    c_work_map = []
    c_jids = []
    for i in range(len(client_list)):
        work_map = {}
        jids = set()
        for r in res_pool[i]:
            if r == None:
                continue
            jid, wid = r
            jids.add(jid)
            work_map[jid] = wid
        c_work_map.append(work_map)
        c_jids.append(jids)

    return c_jids, c_work_map


def _read_job(c, data):
    jid, wid = data
    try:
        if c.finished(jid):
            d = c.result(jid)
            try:
                c.delete(jid)
            except:
                return (jid, wid, d)
            return (jid, wid, d)
    except:
        return None
    return None

def _read_job_client(datas):
    ret_data = []
    c, jids, work_map = datas

    while True:
        wdata = []
        for jid in jids:
            wdata.append((jid, work_map[jid]))

        try:
            res = map(functools.partial(_read_job, c), wdata)

            for r in res:
                if r == None:
                    continue
                jid, wid, d = r
                ret_data.append((wid, d))
                jids.remove(jid)
            if len(jids) == 0:
                break
            time.sleep(len(jids) / 3)
            time.sleep(0.25)
        except Exception as e:
            print(e)
            time.sleep(1)

    print("Client finished: " + c.uri)
    return ret_data


def wait_results(client_list, work_list, c_jids, c_work_map):
    results = {}

    c_zip = []
    for i in range(len(client_list)):
        c_zip.append((client_list[i], c_jids[i], c_work_map[i]))

    pool = Pool(processes=len(client_list))
    res_pool = pool.map(_read_job_client, c_zip)
    for res in res_pool:
        for r in res:
            wid, d = r
            results[wid] = d

    return results

def run(client_list, work_list, kernel_name):
    print("Sending sats...")
    c_jids, c_work_map = _send_sats(client_list, work_list, kernel_name)
    print("Waiting for results...")
    return wait_results(client_list, work_list, c_jids, c_work_map)
