import time
from hash_framework.manager.client import Client

def __main__():
    c = Client("http://localhost:5000")
    d =  {
        "algo": "md4",
        "rounds": 36,
        "cms_args": "",
        "places": [0, 16],
        "h1_start_state": "FTTFFTTTFTFFFTFTFFTFFFTTFFFFFFFTTTTFTTTTTTFFTTFTTFTFTFTTTFFFTFFTTFFTTFFFTFTTTFTFTTFTTTFFTTTTTTTFFFFTFFFFFFTTFFTFFTFTFTFFFTTTFTTF",
        "h2_start_state": "FTTFFTTTFTFFFTFTFFTFFFTTFFFFFFFTTTTFTTTTTTFFTTFTTFTFTFTTTFFFTFFTTFFTTFFFTFTTTFTFTTFTTTFFTTTTTTTFFFFTFFFFFFTTFFTFFTFTFTFFFTTTFTTF",
        "h1_start_block": "FTTTTFFFFTTFFTFTFTTFTTFFFTFFFFFTFTTFFTFTFTTFFTFFFTTFTTTFFTTFFFFTFTTFFFTTFTFTFFTTFFTFFFFFFTTTFFTFFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFFFTTFTTFFFTTFFFFTFFTTTTFFFFTFFFFFFTTFTTTFFTTFFFFTFTTTTFFFFTTFFTFTFFTFTTTFFTTTFFTFFTTFFTFTFTTFFTFFFTTFFFTTFTTTFFTTFFTFTTTFFTTFTTFTFTTFTTFFFTTFFTFTFTTFFTFTFTTFTFFFFTTFFFFTFTTFTTFTFTTFFTTTFTFFFFFFFTTFFFTTFFTFTTTFFTTFTTFFFTTFTFFTFFTFFFFFFFTTTTTFFTTFTTFTFTTFTTTTFTTFTTTTFTTFFFTTFTTFFTFTFTFTFFTTFTFTFFFFFFTFFFFFFTTFFTFFFTTFTTTFFTTFTTFTFTTFTFFTFTTFFTFTFTTTFFTFFFFFTFTFFTTFFTFTFTTFFTTTFTTFFFFT"
    }
    jids = set()
    places = {}
    for i in range(0, 32):
        for j in range(0, 32):
            if j < i:
                continue
            d['places'] = list(set([i, j]))
            jid = c.add_sat("second_preimage", d)
            if jid != False:
                jids.add(jid)
                places[jid] = tuple(d['places'])
            else:
                print(jid)
                print(d['places'])
                print([i, j])

    results = set()
    while True:
        for jid in jids.copy():
            if c.finished(jid):
                jids.remove(jid)
                d = c.result(jid)
                c.delete(jid)
                if d['return'] == 10:
                    results.add(places[jid])
        if len(jids) == 0:
            break
        time.sleep(0.5)
    print(results)

if __name__ == "__main__":
    __main__()
