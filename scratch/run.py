import rca
import cla

import hash_framework

import time

m = hash_framework.models()
m.model_dir = '.'
m.start('models', False)
m.remote = False
hash_framework.models.vars.write_header()

bit_size = 1024
rcaa = []
rcab = []
claa = []
clab = []
for i in range(0, bit_size):
    rcaa.append('rcaa' + str(i))
    rcab.append('rcab' + str(i))
    claa.append('claa' + str(i))
    clab.append('clab' + str(i))

rca.__main__(rcaa, rcab, "rca")
cla.__main__(claa, clab, "cla")


f = open('01-inputs.txt', 'w')
s = "AND("
for i in range(0, bit_size):
    s += "rcaa" + str(i) + " == claa" + str(i) + ","
    s += "rcab" + str(i) + " == clab" + str(i) + ","

s = s[:-1] + ")"
f.write("input := " + s + ";\n")

s = "NOT(AND("
for i in range(0, bit_size):
    s += "rcas" + str(i) + " == clas" + str(i) + ","

s = s[:-1] + "))"
f.write("output := " + s + ";\n")
f.close()

f = open('99-problem.txt', 'w')
f.write("ASSIGN input, output;")
f.close()

m.collapse()
m.build()
t1 = time.time()
m.run(count=1)
t2 = time.time()
print("Run time: " + str(t2-t1))
rs = m.load_results()

for r in rs:
    rcaa = ""
    rcab = ""
    rcas = ""

    claa = ""
    clab = ""
    clas = ""

    for i in range(0, bit_size):
        rcaa += r["rcaa" + str(i)]
        rcab += r["rcab" + str(i)]
        rcas += r["rcas" + str(i)]

        claa += r["claa" + str(i)]
        clab += r["clab" + str(i)]
        clas += r["clas" + str(i)]

    print("ra:" + rcaa + " - rb:" + rcab + " - rs:" + rcas)
    print("ca:" + claa + " - cb:" + clab + " - cs:" + clas)

#print(rs)
