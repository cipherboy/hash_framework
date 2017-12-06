from hash_framework.kernels.abstract import Kernel
from hash_framework.kernels.families import Families
from hash_framework.kernels.neighborhood import Neighborhood
from hash_framework.kernels.zeroes import Zeroes
from hash_framework.kernels.ones import Ones
from hash_framework.kernels.ascii import ASCII
from hash_framework.kernels.multicollision import Multicollision

all_kernels = {
    'abstract': Kernel,
    'families': Families,
    'neighborhood': Neighborhood,
    'zeroes': Zeroes,
    'ones': Ones,
    'ascii': ASCII,
    'multicollision': Multicollision
}

def lookup(name):
    return all_kernels[name]
