#!/usr/bin/env python
# coding=cp936
import sys
cur_docid = ''
cur_info = ''

for line  in sys.stdin:
    arr = line.strip().split('\t')
    docid = arr[0]
    tag = arr[1]
    if cur_docid == docid and tag == '1':
        score = arr[4]
        query = arr[2]
        print '\t'.join([query, cur_info, score])
        continue
    if cur_docid != docid and tag == '0':
        cur_docid = docid
        cur_info = '\t'.join(arr[3:])
