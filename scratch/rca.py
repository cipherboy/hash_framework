#!/usr/bin/env python3

from hash_framework.boolean import *

def __main__():
	f = open('02-rca-2x-4bits.txt', 'w')

	a = ['a1', 'a2', 'a3', 'a4']
	b = ['b1', 'b2', 'b3', 'b4']
	c = 'F'
	s = []
	prefix = 'rca'

	for i in range(0, len(a)):
		a[i] = prefix + a[i]
		b[i] = prefix + b[i]

	i = 3
	s = [clause_dedupe(simplify(('xor', a[i], b[i], c)), prefix)] + s
	c = clause_dedupe(simplify(('xor', ('and', a[i], b[i]), ('and', a[i], c), ('and', b[i], c))), prefix)
	i = 2
	s = [clause_dedupe(simplify(('xor', a[i], b[i], c)), prefix)] + s
	c = clause_dedupe(simplify(('xor', ('and', a[i], b[i]), ('and', a[i], c), ('and', b[i], c))), prefix)
	i = 1
	s = [clause_dedupe(simplify(('xor', a[i], b[i], c)), prefix)] + s
	c = clause_dedupe(simplify(('xor', ('and', a[i], b[i]), ('and', a[i], c), ('and', b[i], c))), prefix)
	i = 0
	s = [clause_dedupe(simplify(('xor', a[i], b[i], c)), prefix)] + s
	c = clause_dedupe(simplify(('xor', ('and', a[i], b[i]), ('and', a[i], c), ('and', b[i], c))), prefix)

	global clause_dedupe_s

	for k in clause_dedupe_s:
		if k[0:len(prefix)] == prefix:
			f.write(k + " := " + translate(clause_dedupe_s[k]) + ";\n")

	for i in range(0, len(s)):
		f.write(prefix + "s" + str(i+1) + " := " + translate(s[i]) + ";\n")


	f.close()
