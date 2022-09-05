#!/usr/bin/env python
# coding=cp936

import sys
import re
pattern1        = re.compile('<terminfos>.*?</terminfos>')
pattern2        = re.compile('<terminfo.*?/>')
pattern_termid  = re.compile('term="(-?\d+)"')
pattern_nimp    = re.compile('NImp="(\d+)"')
pattern_kcw     = re.compile('kcweight="(\d+)"')
pattern_pos     = re.compile('pos="(\d+)"')
pattern_length  = re.compile('len="(\d+)"')
pattern_nquery  = re.compile('<nquery>.*?</nquery>')

for line in open('./part-m-00028'):    #qltr.infer.input
    line_seg = line.strip().split('\t')
    if not line_seg[0]:                 # maybe an empty query
        print '\t\t\t'
        continue
    orig_query = line_seg[0]
    rest = line_seg[1]

    processed_query_match = pattern_nquery.search(rest)
    span = processed_query_match.span()
    processed_query = rest[span[0]+8: span[1]-9]            # half-width

    match = pattern1.search(rest)
    span = match.span()
    terminfo = rest[span[0]+11: span[1]-12]
    terminfo_list = pattern2.findall(terminfo)

    termid_list = []
    kcw_list = [str(0) for i in range(len(processed_query.decode('gb18030')))]
    nimp_list = [str(0) for i in range(len(processed_query.decode('gb18030')))]
    if terminfo_list:                                       # terminfo_list is not empty
        for string in terminfo_list:                        # here is one chinese word '考研'
            # find information
            termid_match = pattern_termid.search(string)
            termid = termid_match.group(1)
            nimp = pattern_nimp.search(string).group(1)
            kcw = int(pattern_kcw.search(string).group(1))
            pos = int(pattern_pos.search(string).group(1))
            length = int(pattern_length.search(string).group(1))

            # save
            termid_list.append(termid)
            kcw_list[pos:pos+length] = [str(float(kcw)/length) for i in range(length)]
            nimp_list[pos:pos+length] = [str(float(nimp)/length) for i in range(length)]
    else:
        sys.stderr.write(line.strip() + '\n')
        
    print processed_query + '\t' + ' '.join(termid_list) + '\t' + ' '.join(kcw_list) + '\t' + ' '.join(nimp_list)
