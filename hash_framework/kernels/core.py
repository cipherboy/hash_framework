from hash_framework.kernels.abstract import Kernel
from hash_framework.kernels.families import Families
from hash_framework.kernels.neighborhood import Neighborhood
from hash_framework.kernels.zeros import Zeros
from hash_framework.kernels.ones import Ones
from hash_framework.kernels.ascii import ASCII
from hash_framework.kernels.multicollision import Multicollision
from hash_framework.kernels.minimal import Minimal

all_kernels = {
    'abstract': Kernel,
    'families': Families,
    'neighborhood': Neighborhood,
    'zeros': Zeros,
    'ones': Ones,
    'ascii': ASCII,
    'multicollision': Multicollision,
    'minimal': Minimal
}

def lookup(name):
    return all_kernels[name]
