#!/usr/bin/env python
# coding=cp936
import sys
from collections import defaultdict
dd = defaultdict(lambda : 0)
for line in sys.stdin:
    arr = line.strip().split('\t')
    cnt = int(arr[1])
    query = arr[0].split('#random_key_lqzh#')[1]
    dd[query] += cnt

for query in dd:
    print query + '\t' + str(dd[query])
    



