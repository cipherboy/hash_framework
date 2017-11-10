#!/usr/bin/env python

from hash_framework.boolean.simplify import *
from hash_framework.boolean.translate import *
from hash_framework.boolean.variables import *
from hash_framework.boolean.core import *

def writeyy(f, prefix, yy, ic, eval_table):
    for i in range(0, 32):
        name = prefix + "i" + str(ic)
        if not yy[i] in ['T', 'F']:
            clause = simplify(yy[i])
            var = clause_dedupe(clause, prefix)
            if not name in eval_table:
                eval_table[name] = var
                if f != None:
                    f.write(name + " := " + var + ";\n")
            elif name in eval_table and f != None:
                printf("Here - name in eval_table: " + eval_table[name])
                if eval_table[name] in ['T', 'F']:
                    f.write(name + " := " + var + ";\n")
                    f.write("etc" + name + " := " + name + " == " + eval_table[name] + ";\n")
                elif type(eval_table[name]) == type(name):
                    print("Here")
                    f.write(eval_table[name] + " := " + var + ";\n")
                else:
                    print("Unknown eval_table entry for `" + name + "`: " + eval_table[name])
        else:
            #print("Here")
            eval_table[name] = yy[i]
            if f != None:
                f.write(name + " := " + yy[i] + ";\n")
        ic += 1
    return ic, eval_table

def write_literal(f, dest, source, eval_table, prefix):
    if not source in ['T', 'F']:
        clause = simplify(source)
        var = clause_dedupe(clause, prefix)
        #print([dest, source, var])
        if not dest in eval_table:
            eval_table[dest] = var
            if f != None:
                f.write(dest + " := " + var + ";\n")
        elif dest in eval_table and f != None:
            if eval_table[dest] in ['T', 'F']:
                f.write(dest + " := " + var + ";\n")
                f.write("etc" + dest + " := " + dest + " == " + eval_table[dest] + ";\n")
            elif type(eval_table[dest]) == type(dest):
                print("Here2")
                f.write(eval_table[dest] + " := " + translate(simplify(source)) + ";\n")
            else:
                print("Unknown eval_table entry for `" + dest + "`: " + eval_table[dest])
    else:
        eval_table[dest] = source

    return eval_table

def writeo(f, prefix, zz, n, eval_table):
    for i in range(0, 32):
        name = prefix + str(n) + str(i)
        if not zz[i] in ['T', 'F']:
            clause = simplify(zz[i])
            var = clause_dedupe(clause, prefix)
            if not name in eval_table:
                eval_table[name] = var
                if f != None:
                    f.write(name + " := " + var + ";\n")
            elif name in eval_table and f != None:
                if eval_table[name] in ['T', 'F']:
                    f.write(name + " := " + var + ";\n")
                    f.write("etc" + name + " := " + name + " == " + eval_table[name] + ";\n")
                elif type(eval_table[name]) == type(name):
                    print("Here2")
                    f.write(eval_table[name] + " := " + translate(simplify(zz[i])) + ";\n")
                else:
                    print("Unknown eval_table entry for `" + name + "`: " + eval_table[name])
        else:
            eval_table[name] = zz[i]
            if f != None:
                f.write(name + " := " + zz[i] + ";\n")
    return eval_table

def buildxx(rc, eval_table, prefix=""):
    xx = []
    for i in range(rc*32, rc*32 + 32):
        name = prefix + "b" + str(i)
        if name in eval_table and type(eval_table[name]) == type('T'):
            xx.append(eval_table[name])
        else:
            xx.append(name)
    return xx

def replace_yy(ic, eval_table, prefix=""):
    aa = []
    for i in range(ic-32, ic):
        name = prefix + "i" + str(i)
        if name in eval_table and type(eval_table[name]) == type('T') and eval_table[name] in ['T', 'F']:
            aa.append(eval_table[name])
        else:
            aa.append(name)
    #print("aa", aa)
    return aa

def print_vars(eval_table, prefix, min, max):
    aa = []
    for i in range(min, max):
        name = prefix + str(i)
        aa.append(eval_table[name])
    print(prefix + "[" + str(min) + "-" + str(max) + "] = " + str(b_tonum(aa)))
