from hash_framework.kernels.abstract import Kernel
from hash_framework.kernels.second_preimage import SecondPreimage
from hash_framework.kernels.neighborhood import Neighborhood

all_kernels = {
    'abstract': Kernel,
    'second_preimage': SecondPreimage,
    'neighborhood': Neighborhood
}

def lookup(name):
    return all_kernels[name]
