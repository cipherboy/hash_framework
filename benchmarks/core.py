from benchmarks.adders import *

def from_name(name):
    if name == 'associativity':
        return Associativity
    if name == 'equality':
        return Equality

def run_benchmark(benchmark):
    print(benchmark)
    cls = from_name(benchmark['name'])
    b = cls(benchmark['args'])
    b.setup()
    r = b.run(benchmark['count'])
    b.clean()
    return r

def run_benchmarks(benchmarks):
    r = []
    for benchmark in benchmarks:
        r.append(run_benchmark(benchmark))

    return r
