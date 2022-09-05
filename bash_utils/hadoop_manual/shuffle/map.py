#!/usr/bin/env python
# coding=cp936
import sys
import random
import time

for line in sys.stdin:
    random.seed(time.time())
    key = '_'.join([str(x) for x in [random.randint(1,1000), random.randint(1,1000), random.randint(1,1000)]])
    line = line.strip()
    print(key + "\t#rand_key#\t" + line) 
