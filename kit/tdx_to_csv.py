#! /usr/bin/env python

import sys
import os
import re
from struct import *

IFN = sys.argv[1]
OFN = sys.argv[2]



tdx_file = open(IFN, 'rb')
buf = tdx_file.read()
tdx_file.close()
 
csv_file = open(OFN,'w')


num = len(buf)
no = num / 32
b = 0
e = 32


csv_file.write('date,open,high,low,close,amount,volume\n')

for i in xrange(no):
    splits = unpack('IIIIIfII', buf[b:e])

    date = str(splits[0])
    open_price = str(splits[1] / 100.0)
    high_price = str(splits[2] / 100.0)
    low_price = str(splits[3] / 100.0)
    close_price = str(splits[4] / 100.0)
    amount = str(splits[5] / 10000.0)
    volume = str(splits[6] / 100)
    reserved = splits[7]

    csv_file.write(','.join([date, open_price, high_price, low_price, close_price, amount, volume]) + '\n')
    b += 32
    e += 32

csv_file.close() 
