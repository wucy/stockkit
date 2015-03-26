#! /usr/bin/env python


import os
import sys
import re
import datetime


togo_folder = sys.argv[1]
rename_folder = sys.argv[2]

files = os.popen('ls %s/*/*day' % (togo_folder)).readlines()

for one in files:
    one = one.strip()
    splits = one.split('/')
    new_name = rename_folder + '/' + splits[-2] + splits[-1]
    cmd = 'cp %s %s' % (one, new_name)
    print cmd
    os.system(cmd)


