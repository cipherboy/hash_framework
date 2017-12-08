from hash_framework.algorithms.md4 import md4
from hash_framework.algorithms.md5 import md5

all_algorithms = {
    'md4': md4,
    'md5': md5,
}

def lookup(name):
    return all_algorithms[name]
