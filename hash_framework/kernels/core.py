from hash_framework.kernels.abstract import Kernel
from hash_framework.kernels.second_preimage import SecondPreimage
from hash_framework.kernels.neighborhood import Neighborhood
from hash_framework.kernels.zeroes import Zeroes
from hash_framework.kernels.ones import Ones
from hash_framework.kernels.ascii import ASCII

all_kernels = {
    'abstract': Kernel,
    'second_preimage': SecondPreimage,
    'neighborhood': Neighborhood,
    'zeroes': Zeroes,
    'ones': Ones,
    'ascii': ASCII,
}

def lookup(name):
    return all_kernels[name]
