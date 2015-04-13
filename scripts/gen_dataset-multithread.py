#! /usr/bin/env python


import os
import sys
import re
import datetime
import threading
import Queue

INIT_TDX_DIR = sys.argv[1]

OUT_DIR_ROOT = sys.argv[2]

MY_LOCAL = 'init'

csv_local = OUT_DIR_ROOT + '/' + MY_LOCAL + '/csv'

plain_local = OUT_DIR_ROOT + '/' + MY_LOCAL + '/plain'


year = 1980

def process_job(stock_tdx):
    #tdx to csv
    stock = stock_tdx.split('/')[-1].split('.')[0] # dir/$stock.day
    stock_csv = csv_local + '/' + stock + '.csv'
    os.system('./kit/tdx_to_csv.py %s %s' % (stock_tdx, stock_csv))
    
    
    #csv to plain and then trimmed
    os.system('./kit/csv_to_plain.py %s %s %s' % (stock_csv, plain_local, stock))

    plain_marco = plain_local + '/' + stock
    trim_len = 0
    #train
    for tset in ['train', 'cv', 'eval']:
        os.system('./kit/trim_plain.py %s.%s %s.%s.trim %d %d' % (plain_marco, tset, plain_marco, tset, year, trim_len))


   

class pc_worker(threading.Thread):
    def __init__(self, queue, name = "WORKER", time_out = 1):
        threading.Thread.__init__(self)
        self.queue = queue
        self.is_stop = False
        self.name = name
        self.time_out = time_out
        #self.log = list()

    def run(self):
        while not self.is_stop or self.queue.qsize() != 0:
            if (self.is_stop):
                if self.queue.qsize() != 0:
                    pass
                    #print '[%s]%s Waiting %d item(s) in queue.' % (self.name, time.ctime(), self.queue.qsize())a
                else:
                    #print '[%s] Stopping ...' % (self.name)
                    break
            cmd = None
            try:
                cmd = self.queue.get(True, self.time_out)
            except:
                #print '[%s]%s Queue is empty, waiting...' % (self.name, time.ctime())
                continue
            
            process_job(cmd)            
            #log = (cmd, os.popen(cmd).readlines())
            #self.log.append(log)

    def stop(self):
        self.is_stop = True


class pc_scheduler:
    def __init__(self, num_worker):
        self.queue = Queue.Queue()
        self.worker_list = list()
        for i in range(num_worker):
            worker = pc_worker(self.queue, "WORKER" + str(i))
            worker.setDaemon(True)
            self.worker_list.append(worker)
            worker.start()

    def add_job(self, cmd):
        self.queue.put(cmd)

    def wait(self):
        for worker in self.worker_list:
            worker.stop()
        for worker in self.worker_list:
            worker.join()





todolst = os.popen('ls %s/sh60*day %s/sz30*day %s/sz00*day' % (INIT_TDX_DIR, INIT_TDX_DIR, INIT_TDX_DIR)).readlines()

#print todolst

os.system('mkdir -p %s' % (csv_local))
os.system('mkdir -p %s' % (plain_local))


print 'TOTAL STOCK =', len(todolst)


scheduler = pc_scheduler(100)

for stock in todolst:
    stock_tdx = stock.strip()
    #print stock_tdx
    #process_job(stock_tdx)    

    scheduler.add_job(stock_tdx)

scheduler.wait()


for tset in ['train', 'cv', 'eval']:
    merge_plain = OUT_DIR_ROOT + '/' + MY_LOCAL + '/' + tset + '.plain'
    #print merge_plain
    os.system('cat %s/*%s.trim > %s' % (plain_local, tset, merge_plain))

    merge_xgb = OUT_DIR_ROOT + '/' + MY_LOCAL + '/' + tset + '.xgb'
    os.system('kit/plain_to_xgb.py %s %s' % (merge_plain, merge_xgb))
