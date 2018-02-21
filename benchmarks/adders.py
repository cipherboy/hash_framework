from benchmarks.abstract import Benchmark
import hash_framework as hf

import time

class Associativity(Benchmark):
    name = 'associativity'

    def __init__(self, args):
        self.args = args
        self.adder_cfg = args['adder_cfg']
        self.bits = args['bits']
        self.m = None

    def setup(self):
        hf.config.default_adder = self.adder_cfg

        m = hf.models()
        m.remote = False
        m.start("benchmark-associativity-" + str(self.bits), True)
        hf.models.vars.write_header()

        a = ['a' + str(i) for i in range(0, self.bits)]
        b = ['b' + str(i) for i in range(0, self.bits)]
        c = ['c' + str(i) for i in range(0, self.bits)]
        d = ['d' + str(i) for i in range(0, self.bits)]

        print(a)

        lo1, _ = hf.boolean.b_addl('lo1', a, b)
        lo2, _ = hf.boolean.b_addl('lo2', lo1, c)
        lo3, _ = hf.boolean.b_addl('lo3', lo2, d)

        ro1, _ = hf.boolean.b_addl('ro1', c, d)
        ro2, _ = hf.boolean.b_addl('ro2', b, ro1)
        ro3, _ = hf.boolean.b_addl('ro3', a, ro2)

        to1, _ = hf.boolean.b_addl('to1', a, b)
        to2, _ = hf.boolean.b_addl('to2', c, d)
        to3, _ = hf.boolean.b_addl('to3', to1, to2)

        hf.models.vars.write_dedupe(name="01-dedupe.txt")
        equality = ['and']
        for i in range(0, self.bits):
            equality.append(('equal', lo3[i], ro3[i]))
            equality.append(('equal', lo3[i], to3[i]))
            equality.append(('equal', ro3[i], to3[i]))

        equality = tuple(equality)
        hf.models.vars.write_clause('equality', ('not', equality), '98-problem.txt')
        hf.models.vars.write_assign(['equality'])
        m.collapse()
        m.build()
        self.m = m

        self.lo3 = lo3
        self.ro3 = ro3
        self.to3 = to3

    def _error(self):
        for r in self.m.load_results():
            a = []
            b = []
            c = []
            d = []
            lo3 = []
            ro3 = []
            to3 = []
            for i in range(0, self.bits):
                a.append(r['a' + str(i)])
            for i in range(0, self.bits):
                b.append(r['b' + str(i)])
            for i in range(0, self.bits):
                c.append(r['c' + str(i)])
            for i in range(0, self.bits):
                d.append(r['d' + str(i)])
            for v in self.lo3:
                lo3.append(r[v])
            for v in self.ro3:
                ro3.append(r[v])
            for v in self.to3:
                to3.append(r[v])
            print((a, b, c, d))
            print((lo3, ro3, to3))
            print("\n")

    def _time(self):
        t1 = time.time()
        r = self.m.run()
        if r:
            self._error()

        assert(r == False)
        return time.time() - t1

    def run(self, count):
        r = []
        for i in range(0, count):
            nt = self._time()
            o = {}
            o['args'] = self.args
            o['name'] = self.name
            o['run'] = i+1
            o['count'] = count
            o['time'] = nt
            r.append(o)

        return r
