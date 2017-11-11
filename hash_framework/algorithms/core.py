from hash_framework.algorithms.md4 import md4

all_algorithms = {
    'md4': md4
}

def lookup(name):
    return all_algorithms[name]
