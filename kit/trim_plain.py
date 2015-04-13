#! /usr/bin/env python

import sys




IN_PLAIN = sys.argv[1]
OUT_TRIM_PLAIN = sys.argv[2]

START_TIME = sys.argv[3]
TRIM_LEN = int(sys.argv[4])

full_start_time = START_TIME + '0' * (8 - len(START_TIME))
#print full_start_time

plain_fp = open(IN_PLAIN, 'r')
plain_lines = plain_fp.readlines()
plain_fp.close()


trim_fn = OUT_TRIM_PLAIN

tfp = open(trim_fn, 'w')

for i in range(TRIM_LEN, len(plain_lines)):
    line = plain_lines[i].strip()
    [newline, time] = line.split('#')
    if time <= START_TIME:
        continue
    tfp.write(newline + '\n')

tfp.close()



