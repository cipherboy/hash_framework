#!/usr/bin/env python3

import hash_framework as hf
import requests

api = 'http://localhost:1325'

def tc_api_create_task():
    r = requests.post(api + '/tasks/', json=[{'name': 'test-1', 'algo': 'md4'}, {'name': 'test-2', 'algo': 'md5'}])
    assert(r.status_code == 200)

    return True


def tc_api_create_host():
    r = requests.post(api + '/hosts/', json={'ip': '127.0.0.1', 'hostname': 'localhost', 'cores': 4, 'memory': 16288468, 'disk': 419343296, 'version': 'faa6a5d87eb63465d0628ac8f264e478aedc5352', 'in_use': True})
    assert(r.status_code == 200)

    return True


def __main__():
    tests = [tc_api_create_task, tc_api_create_host]

    for test in tests:
        ret = test()
        if ret:
            print(test.__name__ + "... OK")
        else:
            print(test.__name__ + "... Failed")
            break

if __name__ == "__main__":
    __main__()
