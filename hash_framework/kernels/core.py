from hash_framework.kernels.abstract import Kernel
from hash_framework.kernels.second_preimage import SecondPreimage

all_kernels = {
    'abstract': Kernel,
    'second_preimage': SecondPreimage
}

def lookup(name):
    return all_kernels[name]
