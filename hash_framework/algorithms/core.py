from hash_framework.algorithms.md4 import md4
from hash_framework.algorithms.md5 import md5
from hash_framework.algorithms.sha1 import sha1
from hash_framework.algorithms.sha3 import sha3
from hash_framework.algorithms.siphash import siphash

all_algorithms = {
    "md4": md4,
    "md5": md5,
    "sha1": sha1,
    "sha3": sha3,
    "siphash": siphash,
}


def lookup(name):
    return all_algorithms[name]


def resolve(name):
    if isinstance(name, str):
        name = lookup(name)

    return name()
