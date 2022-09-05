#!/usr/bin/env python
# coding=cp936
import urllib
import sys


import random
dd = {}
with open('query.txt') as f:
    for line in f:
        line = line.strip()
        dd[line] = 0
for line in sys.stdin:
    query_code = line.strip().split('\t')[1]
    query =  urllib.unquote_plus(query_code)
    if query in dd:
        dd[query] +=1

for query in dd:
    if dd[query] > 0:
        print str(random.randint(0,200)) + '#random_key_lqzh#' + query + '\t' + str(dd[query])
