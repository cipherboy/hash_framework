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
        m.start("benchmark-adders-associativity-" + str(self.bits), True)
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
            o['run'] = i+1
            o['count'] = count
            o['time'] = nt
            r.append(o)

        return r


class Equality(Benchmark):
    name = 'equality'

    def __init__(self, args):
        self.args = args
        self.adder_cfg = args['adder_cfg']
        self.bits = args['bits']
        self.shape = args['shape']
        self.m = None

    def setup(self):
        hf.config.default_adder = self.adder_cfg

        m = hf.models()
        m.remote = False
        m.start("benchmark-adders-equality-" + str(self.bits), True)
        hf.models.vars.write_header()

        la = ['la' + str(i) for i in range(0, self.bits)]
        lb = ['lb' + str(i) for i in range(0, self.bits)]
        lc = ['lc' + str(i) for i in range(0, self.bits)]
        ld = ['ld' + str(i) for i in range(0, self.bits)]

        ra = ['ra' + str(i) for i in range(0, self.bits)]
        rb = ['rb' + str(i) for i in range(0, self.bits)]
        rc = ['rc' + str(i) for i in range(0, self.bits)]
        rd = ['rd' + str(i) for i in range(0, self.bits)]

        lo1 = None
        lo2 = None
        lo3 = None

        ro1 = None
        ro2 = None
        ro3 = None

        if self.shape == 'tree':
            lo1, _ = hf.boolean.b_addl('lo1', la, lb)
            lo2, _ = hf.boolean.b_addl('lo2', lc, ld)
            lo3, _ = hf.boolean.b_addl('lo3', lo1, lo2)

            ro1, _ = hf.boolean.b_addl('ro1', ra, rb)
            ro2, _ = hf.boolean.b_addl('ro2', rc, rd)
            ro3, _ = hf.boolean.b_addl('ro3', ro1, ro2)
        elif self.shape == 'left':
            lo1, _ = hf.boolean.b_addl('lo1', la, lb)
            lo2, _ = hf.boolean.b_addl('lo2', lo1, lc)
            lo3, _ = hf.boolean.b_addl('lo3', lo2, ld)

            ro1, _ = hf.boolean.b_addl('ro1', ra, rb)
            ro2, _ = hf.boolean.b_addl('ro2', ro1, rc)
            ro3, _ = hf.boolean.b_addl('ro3', ro2, rd)
        elif self.shape == 'right':
            lo1, _ = hf.boolean.b_addl('lo1', lc, ld)
            lo2, _ = hf.boolean.b_addl('lo2', lb, lo1)
            lo3, _ = hf.boolean.b_addl('lo3', la, lo2)

            ro1, _ = hf.boolean.b_addl('ro1', rc, rd)
            ro2, _ = hf.boolean.b_addl('ro2', rb, ro1)
            ro3, _ = hf.boolean.b_addl('ro3', ra, ro2)


        hf.models.vars.write_dedupe(name="01-dedupe.txt")
        equality = ['and']
        for i in range(0, self.bits):
            equality.append(('equal', lo3[i], ro3[i]))

        equality = tuple(equality)
        hf.models.vars.write_clause('equality', equality, '50-equality.txt')

        diff_input = ['or']
        for i in range(0, self.bits):
            diff_input.append(('not', ('equal', la[i], ra[i])))
            diff_input.append(('not', ('equal', lb[i], rb[i])))
            diff_input.append(('not', ('equal', lc[i], rc[i])))
            diff_input.append(('not', ('equal', ld[i], rd[i])))
        diff_input = tuple(diff_input)
        hf.models.vars.write_clause('input', diff_input, '60-input.txt')

        hf.models.vars.write_assign(['equality', 'input'])
        m.collapse()
        m.build()
        self.m = m

        self.lo3 = lo3
        self.ro3 = ro3

    def _error(self):
        pass

    def _time(self):
        t1 = time.time()
        r = self.m.run()
        if not r:
            self._error()

        assert(r == True)
        return time.time() - t1

    def run(self, count):
        r = []
        for i in range(0, count):
            nt = self._time()
            o = {}
            o['run'] = i+1
            o['count'] = count
            o['time'] = nt
            r.append(o)

        return r
