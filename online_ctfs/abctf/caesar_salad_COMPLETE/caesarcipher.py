#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: john
# @Date:   2016-03-10 19:57:46
# @Last Modified by:   john
# @Last Modified time: 2016-08-12 12:07:39

import string
import collections


def rotate(rotate_string, number_to_rotate_by):

    upper = collections.deque(string.ascii_uppercase)
    lower = collections.deque(string.ascii_lowercase)

    upper.rotate(number_to_rotate_by)
    lower.rotate(number_to_rotate_by)

    upper = ''.join(list(upper))
    lower = ''.join(list(lower))

    return rotate_string.translate(string.maketrans(string.ascii_uppercase, upper)).translate(string.maketrans(string.ascii_lowercase, lower))


for i in range(26):
    print i, rotate("xyzqc{t3_qelrdeq_t3_k33a3a_lk3_lc_qe3p3}", i)
