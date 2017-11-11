from hash_framework.config import config
from hash_framework.boolean.translate import *
from hash_framework.utils import *

import os, collections

class models:
    def __init__(self):
        self.cms_bin = config.cms_bin
        self.cms_args = config.cms_args
        self.bc_bin = config.bc_bin
        self.bc_args = config.bc_args
        self.model_dir = config.model_dir
        self.remote = True

    def get_mapping(self, cnf="problem.cnf"):
        var_mapping = collections.defaultdict(list)

        f_cnf = open(cnf, 'r')

        for l in f_cnf:
            if len(l) > 0 and l[0] == 'c' and ' <-> ' in l:
                l_var = l[1:].split(' <-> ')
                l_var[0] = l_var[0].strip()
                l_var[1] = l_var[1].strip()
                var_mapping[l_var[1]].append(l_var[0])

        return dict(var_mapping)

    def load_results(self, var_mapping=None, out="problem.out", cnf="problem.cnf"):
        f_out = open(out, 'r')
        if var_mapping == None:
            var_mapping = self.get_mapping(cnf=cnf)
        results = []
        result = None
        for l in f_out:
            if l[0] == 's':
                if result != None:
                    results.append(result)
                result = {}
            if l[0] == 'v':
                end = -2
                if l[end] == '0':
                    end = -3
                l_assigns = l[2:end].split(' ')
                for v in l_assigns:
                    var = v
                    val = 'T'
                    if v[0] == '-':
                        var = v[1:]
                        val = 'F'
                    if var in var_mapping:
                        for loc in var_mapping[var]:
                            result[loc] = val
        if result != None and result != {}:
            results.append(result)

        return results

    def generate_raw(algo, prefixes, rounds=None):
        if rounds is None:
            rounds = algo.rounds

        for prefix in prefixes:
            algo.generate([prefix], rounds=rounds)

    def generate(algo, prefixes, rounds=None, bypass=False):
        if rounds is None:
            rounds = algo.rounds

        if bypass:
            models.generate_raw(algo, prefixes, rounds)
            return

        d = models.model_dir + "/cache"
        for prefix in prefixes:
            missing = True
            if os.path.isdir(d):
                missing = False
                for fr in algo.generate_files:
                    f = fr % prefix
                    if not os.path.isfile(d + "/" + f):
                        missing = True

            if missing:
                cd = os.getcwd()
                os.system("mkdir -p " + models.model_dir + "/cache")
                os.chdir(models.model_dir + "/cache")
                algo.generate([prefix], rounds=rounds)
                os.chdir(cd)

            for fr in algo.generate_files:
                f = fr % prefix
                os.system("cp " + d + "/" + f + " " + f)

    def start(self, dir, recreate=False):
        assert(type(dir) == str)

        if recreate:
            os.system("rm -rf " + self.model_dir + "/" + dir)

        os.system("mkdir -p " + self.model_dir + "/" + dir)
        os.chdir(self.model_dir + "/" + dir)

    def build(self, bc="problem.bc", cnf="problem.cnf"):
        assert(type(bc) == str)
        assert(type(cnf) == str)

        ec = subprocess.call([self.bc_bin] + self.bc_args + [bc, cnf])
        count = 0
        while count < 5 and ec != 0:
            ec = subprocess.call([self.bc_bin] + self.bc_args + [bc, cnf])
            count += 1

        if ec != 0 and not os.path.exists(cnf):
            print(os.getcwd())
            print([self.bc_bin] + self.bc_args + [bc, cnf])
            assert(ec == 0)

    def results_json(self, algo, filename, prefixes=["h1", "h2"]):
        objs = json.load(open(filename, 'r'))
        assert(type(objs) == list)
        r = []
        for result in objs:
            assert(type(result) == dict)
            d = {}
            for prefix in prefixes:
                e = prefix_keys(algo.sanitize(unprefix_keys(result, prefix)), prefix)
                d = merge_dict([d, e])
            r.append(d)
        return r

    def results(self, algo, results=None, prefixes=["h1", "h2"], out="problem.out", cnf="problem.cnf"):
        if results == None:
            results = self.load_results(out=out, cnf=cnf)
        r = []
        for result in results:
            d = {}
            for prefix in prefixes:
                e = prefix_keys(algo.sanitize(unprefix_keys(result, prefix)), prefix)
                d = merge_dict([d, e])
            r.append(d)
        return r

    def collapse(self, bc="problem.bc"):
        os.system("cat *.txt > " + bc)

    def run(self, count=10000, random=0, bc="problem.bc", cnf="problem.cnf", output="problem.out"):
        if self.remote:
            return self.run_remote(count, random, bc, cnf, output)

        self.build(bc, cnf)
        f_out = open(output, 'w')
        n_p = subprocess.Popen([self.cms_bin, "--maxsol", str(count), cnf], stdout=f_out)
        r_c = n_p.wait()
        if r_c == 10:
            print("SAT")
            return True
        elif r_c == 20:
            print("UNSAT")
            return False
        else:
            print("UNKNOWN: " + str(r_c))
            return False

    def run_remote(self, count=10000, random=0, bc="problem.bc", cnf="problem.cnf", output="problem.out"):
        self.build(bc, cnf)
        return compute.perform_sat(cnf, output, count, random)

    class vars:
        def write_header(name="00-header.txt", mode="w"):
            f = open(name, mode)
            f.write("BC1.1\n")
            f.flush()
            f.close()

        def write_assign(vars, name="99-problem.txt", mode='w'):
            f = open(name, mode)
            f.write("ASSIGN " + ','.join(vars) + ";\n")
            f.flush()
            f.close()


        def write_values(vars, prefix, name, mode='w'):
            f = open(name, mode)
            i = 0
            for v in vars:
                f.write(prefix + str(i) + ' := ' + v + ";\n")
                i += 1
            f.flush()
            f.close()

        def write_clauses(vars, prefix, name, mode='w'):
            f = open(name, mode)
            i = 0
            for v in vars:
                f.write(prefix + str(i) + ' := ' + translate(v) + ";\n")
                i += 1
            f.flush()
            f.close()

        def write_clause(clause, value, name, mode='w'):
            f = open(name, mode)
            f.write(clause + ' := ' + translate(value) + ";\n")
            f.flush()
            f.close()

        def compute_ddelta(v1, v2):
            assert(len(v1) == len(v2))

            d = ""
            for j in range(0, len(v1)):
                if v1[j] == v2[j]:
                    d += '.'
                elif v1[j] == 'T' and v2[j] == 'F':
                    d += '-'
                elif v1[j] == 'F' and v2[j] == 'T':
                    d += '+'
            return d

        def compute_rdelta(v1, v2):
            assert(len(v1) == len(v2))

            d = ""
            for j in range(0, len(v1)):
                if v1[j] == v2[j]:
                    d += '.'
                else:
                    d += '*'
            return d

        def differential(delta, avar, aoffset, bvar, boffset):
            r = ["and"]
            for i in range(0, len(delta)):
                if delta[i] == '*':
                    r.append(("not", ("equal", avar + str(aoffset + i), bvar + str(boffset + i))))
                elif delta[i] == '.':
                    r.append(("equal", avar + str(aoffset + i), bvar + str(boffset + i)))
                elif delta[i] == '+':
                    r.append(("and", ("equal", avar + str(aoffset + i), 'F'), ("equal", bvar + str(boffset + i), 'T')))
                elif delta[i] == '-':
                    r.append(("and", ("equal", avar + str(aoffset + i), 'T'), ("equal", bvar + str(boffset + i), 'F')))
                elif delta[i] == 'T':
                    r.append(("and", ("equal", avar + str(aoffset + i), 'T'), ("equal", bvar + str(boffset + i), 'T')))
                elif delta[i] == 'F':
                    r.append(("and", ("equal", avar + str(aoffset + i), 'F'), ("equal", bvar + str(boffset + i), 'F')))
            if len(r) == 1:
                r.append(("equal", 'T', 'T'))
            return tuple(r)

        def differentials(dlist):
            r = ["and"]
            for e in dlist:
                delta = e[0]
                avar=e[1]
                aoffset=e[2]
                bvar=e[3]
                boffset=e[4]
                r.append(models.vars.differential(delta, avar, aoffset, bvar, boffset))
            return tuple(r)

        def negated_differentials(dlist):
            r = ["and"]
            for e in dlist:
                delta = e[0]
                avar=e[1]
                aoffset=e[2]
                bvar=e[3]
                boffset=e[4]
                r.append(('not', models.vars.differential(delta, avar, aoffset, bvar, boffset)))
            return tuple(r)

        def choice_differentials(dlist):
            r = ["or"]
            for e in dlist:
                delta = e[0]
                avar=e[1]
                aoffset=e[2]
                bvar=e[3]
                boffset=e[4]
                r.append(models.vars.differential(delta, avar, aoffset, bvar, boffset))
            return tuple(r)

        def any_difference(l, avar="h1b", aoffset=0, bvar="h2b", boffset=0, name="cdiff"):
            r = ["and"]
            for i in range(0, l):
                r.append(('equal', avar + str(aoffset + i), bvar + str(boffset + i)))
            return ('not', tuple(r))
