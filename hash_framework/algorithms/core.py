from hash_framework.algorithms.md4 import md4
from hash_framework.algorithms.md5 import md5
from hash_framework.algorithms.sha3 import sha3

all_algorithms = {
    'md4': md4,
    'md5': md5,
    'sha3': sha3,
}

def lookup(name):
    return all_algorithms[name]
