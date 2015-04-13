#! /usr/bin/env python


import os
import sys
import re
import datetime

INIT_TDX_DIR = sys.argv[1]

OUT_DIR_ROOT = sys.argv[2]

MY_LOCAL = 'init'

csv_local = OUT_DIR_ROOT + '/' + MY_LOCAL + '/csv'

plain_local = OUT_DIR_ROOT + '/' + MY_LOCAL + '/plain'


todolst = os.popen('ls %s/sh60*day %s/sz30*day %s/sz00*day' % (INIT_TDX_DIR, INIT_TDX_DIR, INIT_TDX_DIR)).readlines()

#print todolst

os.system('mkdir -p %s' % (csv_local))
os.system('mkdir -p %s' % (plain_local))


print 'TOTAL STOCK =', len(todolst)

for stock in todolst:
    stock_tdx = stock.strip()
    #print stock_tdx
    
    #tdx to csv
    stock = stock_tdx.split('/')[-1].split('.')[0] # dir/$stock.day
    stock_csv = csv_local + '/' + stock + '.csv'
    os.system('./kit/tdx_to_csv.py %s %s' % (stock_tdx, stock_csv))
    
    
    #csv to plain and then trimmed
    os.system('./kit/csv_to_plain.py %s %s %s' % (stock_csv, plain_local, stock))

    plain_marco = plain_local + '/' + stock
    year = 2014
    trim_len = 0
    #train
    for tset in ['train', 'cv', 'eval']:
        os.system('./kit/trim_plain.py %s.%s %s.%s.trim %d %d' % (plain_marco, tset, plain_marco, tset, year, trim_len))



for tset in ['train', 'cv', 'eval']:
    merge_plain = OUT_DIR_ROOT + '/' + MY_LOCAL + '/' + tset + '.plain'
    #print merge_plain
    os.system('cat %s/*%s.trim > %s' % (plain_local, tset, merge_plain))

    merge_xgb = OUT_DIR_ROOT + '/' + MY_LOCAL + '/' + tset + '.xgb'
    os.system('kit/plain_to_xgb.py %s %s' % (merge_plain, merge_xgb))
