import hash_framework.kernels as kernels

all_kernels = {
    'abstract': kernels.Kernel,
    'second_preimage': kernels.SecondPreimage
}

def lookup(name):
    return all_kernels[name]
