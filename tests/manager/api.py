#!/usr/bin/env python3

import hash_framework as hf
import requests

api = 'http://localhost:1325'

def tc_api_create_task():
    r = requests.post(api + '/tasks', data = [{'name': 'test-1', 'algo': 'md4'}, {'name': 'test-2', 'algo': 'md5'}])
    assert(r.status_code == 200)

    return True
    

def __main__():
    tests = [tc_api_create_task]

    for test in tests:
        ret = test()
        if ret:
            print(test.__name__ + "... OK")
        else:
            print(test.__name__ + "... Failed")
            break

if __name__ == "__main__":
    __main__()
