import rca
import cla

import hash_framework

m = hash_framework.models()
m.model_dir = '.'
m.start('models', False)
m.remote = False
hash_framework.models.vars.write_header()

rca.__main__()
cla.__main__()

f = open('01-inputs.txt', 'w')
f.write("input := AND(rcaa1 == claa1, rcaa2 == claa2, rcaa3 == claa3, rcaa4 == claa4, rcab1 == clab1, rcab2 == clab2, rcab3 == clab3, rcab4 == clab4);\n")
f.write("output := NOT(AND(rcas1 == clas1, rcas2 == clas2, rcas3 == clas3, rcas4 == clas4));\n")
f.close()

f = open('99-problem.txt', 'w')
f.write("ASSIGN input, output;")
f.close()

m.collapse()
m.build()
m.run(count=1)
rs = m.load_results()

for r in rs:
	a = ""
	b = ""
	rcas = ""
	clas = ""

	for i in range(1, 5):
		a += r["rcaa" + str(i)]
		b += r["rcab" + str(i)]
		rcas += r["rcas" + str(i)]
		clas += r["clas" + str(i)]

	print("a:" + a + " - b:" + b + " - rs:" + rcas + " - cs:" + clas)
#print(rs)
