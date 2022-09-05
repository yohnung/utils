#!/usr/bin/env python
# coding=cp936
import sys

for line in sys.stdin:
    line = line.strip().split('\t#rand_key#\t')
    print(''.join(line[1:]))
pass
