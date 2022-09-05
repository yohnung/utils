#!/usr/bin/env python
# coding=cp936
import sys
import numpy as np

num = 0
exp_uniformity = 0
ebd_file = sys.argv[1]
with open(ebd_file) as file:
    for line in file:
        line_seg = line.strip().split('\t')
        data_point1 = list(float(x) for x in line_seg[7].split(' '))
        data_point1 = np.asarray(data_point1) / np.linalg.norm(data_point1)
        try:
            line_seg = next(file).strip().split('\t')
            data_point2 = list(float(x) for x in line_seg[7].split(' '))
            data_point2 = np.asarray(data_point2) / np.linalg.norm(data_point2)

            diff = np.linalg.norm(data_point1 - data_point2)
            exp_uniformity += np.exp(- 2 * diff * diff)
            num += 1
        except:
            pass

uniformity = np.log(exp_uniformity/num)
print "NUM is %s, Uniformity is %s" % (num, uniformity)

