import hash_framework.algorithms as algorithms

all_algorithms = {
    'md4': algorithms.md4
}

def lookup(name):
    return all_algorithms[name]
