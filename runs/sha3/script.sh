#!/bin/bash

rm /tmp/t*.png

python3 ./extract-margins.py 40 t
python3 ./extract-margins.py 75 r
python3 ./extract-margins.py 76 p
python3 ./extract-margins.py 77 c

python3 ./extract-margins.py 41 tr
python3 ./extract-margins.py 42 trp
python3 ./extract-margins.py 43 trpc
python3 ./extract-margins.py 52 trpci0-t
python3 ./extract-margins.py 53 trpci0-tr
python3 ./extract-margins.py 54 trpci0-trp
python3 ./extract-margins.py 55 trpci0-trpc

python3 ./extract-differences.py 56 t
python3 ./extract-differences.py 57 r
python3 ./extract-differences.py 58 p
python3 ./extract-differences.py 59 c

python3 ./extract-id-margins.py 61 t
python3 ./extract-id-margins.py 69 tr
python3 ./extract-id-margins.py 70 trp
python3 ./extract-id-margins.py 71 trpc
python3 ./extract-id-margins.py 72 trpci0-t

python3 ./extract-od-margins.py 64 c
python3 ./extract-od-margins.py 65 pc
python3 ./extract-od-margins.py 67 rpc
python3 ./extract-od-margins.py 68 trpc
python3 ./extract-od-margins.py 73 c-trpc
