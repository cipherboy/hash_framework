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

    c_work_map = []
    c_jids = []
    for i in range(len(client_list)):
        work_map = {}
        for pos in range(len(res_pool[i])):
            if res_pool[i][pos] == None:
                continue
            wid = c_work[i][pos]
            jid = res_pool[i][pos]
            work_map[jid] = wid
        c_work_map.append(work_map)
        c_jids.append(res_pool[i])

    return c_jids, c_work_map


def _read_job(args):
    c_uri, jids = datas
    c = Client(c_uri)
    return

def _read_jobs_client(datas):
    ret_data = []
    c, jids, work_map = datas

    except_count = 0
    while True:
        try:
            j_results = c.bulk_result(jids)
            for k in j_results:
                jids.remove(k)
                ret_data.append((work_map[k], j_results[k]))
                c.delete(k)

            if len(jids) == 0:
                break

            if len(jids) > 10:
                time.sleep(len(jids) * 0.2)
            else:
                time.sleep(0.5)
        except:
            except_count += 1
            print(e)
            time.sleep(1)
            if except_count > 10:
                print("Client had too many exceptions: " + c.uri)
                return ret_data

    print("Client finished: " + c.uri)
    return ret_data


def wait_results(client_list, work_list, c_jids, c_work_map):
    results = {}

    c_zip = []
    for i in range(len(client_list)):
        c_zip.append((client_list[i], c_jids[i], c_work_map[i]))

    pool = Pool(processes=len(client_list))
    res_pool = pool.map(_read_jobs_client, c_zip)
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
