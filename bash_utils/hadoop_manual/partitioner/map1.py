#!/usr/bin/env python
# coding=cp936
import sys
for line in sys.stdin:
    arr = line.strip().split('\t')
    if len(arr) == 4:
        query = arr[0]
        title = arr[1]
        docid = arr[2]
        score = arr[3]
        print '\t'.join([docid, '1', query, title, score])
    if len(arr) == 5:
        query, title, docid, kw1, kw2 = line.strip().split('\t')
        print '\t'.join([docid, '0', query, title,docid, kw1, kw2])

