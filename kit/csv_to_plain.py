#! /usr/bin/env python

import sys
import os
import re
import math

#fix precision for global usage
EPS = 1e-6

#for calc traincv label, what is a zhang instance?
pred_period = 15
pred_avg_inc_rate = 0.03
high_inc_rate = 0.05

#for train / cv splitting, $cv_rate% of the last period of traincv as cv
cv_rate = 0.05


date_id = 0
open_price_id = 1
high_price_id = 2
low_price_id = 3
close_price_id = 4
amount_id = 5
volume_id = 6


def get_traincv_label(stream, stream_id):
#1 increase
#0 decrease
    x = stream[stream_id + pred_period] #checking if out_of_boundary
    

    #if stream[stream_id + 1][low_price_id] > stream[stream_id][close_price_id]:
    #    #zhang, dan shi mai bu liao
    #    return '1'


    sat_peak_price = False
    avg_pred_period = 0
    for i in range(stream_id + 1, stream_id + pred_period + 1):
        avg_pred_period += stream[i][close_price_id]
        if stream[stream_id][close_price_id] * (1 + high_inc_rate) <= stream[i][high_price_id]:
            sat_peak_price = True
    avg_pred_period /= pred_period
    
    if avg_pred_period <= stream[stream_id][close_price_id] * (1 + pred_avg_inc_rate):
        return '1'

    if not sat_peak_price:
        return '1'
    else:
        return '0'


def ema(hist, alpha = None):
    if alpha == None:
        alpha = 2.0 / (len(hist) + 1)
    ret = hist[0]
    #print hist
    #print ret
    for i in range(1, len(hist)):
        ret = alpha * hist[i] + (1 - alpha) * ret
        #print ret
    return ret

def rsi(hist):
    U = list()
    D = list()
    for i in range(1, len(hist)):
        diff = hist[i] - hist[i - 1]
        if diff > 0:
            U.append(abs(diff))
            D.append(0.0)
        else:
            U.append(0.0)
            D.append(abs(diff))
    ema_u = ema(U)
    ema_d = ema(D)
    #div zero
    #print U
    #print D
    #print ema_u
    #print ema_d
    if ema_u + ema_d < EPS:
        return 0.5
    else:
        return ema_u / (ema_u + ema_d)

def max(hist):
    ret = hist[0]
    for i in hist:
        if i > ret:
            ret = i
    return ret

def min(hist):
    ret = hist[0]
    for i in hist:
        if i < ret:
            ret = i
    return ret

def rsv(cur_close, hist_high, hist_low):
    #rsv:
    rsv = 0.5
    hn_ln = max(hist_high) - min(hist_low)
    #print hn_ln
    #exit(0)
    if hn_ln > EPS:
        rsv = (cur_close - min(hist_low)) / hn_ln
    
    return rsv


def dec_pred_len(hist):
# days of successive decrease
    ret = 0.0

    for i in range(len(hist) - 1, 0, -1):
        if hist[i] < hist[i - 1]:
            ret += 1
        else:
            break
    return ret


def get_hist(stream, now, append_hist_len, id_spec = -1):
    ret_hist = []
    for i in range(now - append_hist_len, now + 1):
        hist_id = i
        if hist_id < 0:
            hist_id = 0
        if id_spec == -1:
            ret_hist.append(stream[hist_id])
        else:
            ret_hist.append(stream[hist_id][id_spec])
    return ret_hist

def csv_to_stream(csv_fn):
    ret_stream = list()
    fp = open(csv_fn, 'r')
    raws = fp.readlines()[1:]
    fp.close()
    for line in raws:
        splits = line.strip().split(',')
        item = [splits[0], float(splits[1]), float(splits[2]), float(splits[3]), float(splits[4]), float(splits[5]), float(splits[6])]
        ret_stream.append(item)
    return ret_stream


def get_instance(stream, stream_id, append_hist_len, if_label):
    label = '-1'
    if if_label:
        label = get_traincv_label(stream, stream_id)
    
    ret_inst = list()
    ret_inst.append(label)

    #lots of features
    for i in range(append_hist_len + 1):
        #rsi
        ret_inst.append(rsi(get_hist(stream, stream_id, 6, close_price_id))) #rsi 6
        ret_inst.append(rsi(get_hist(stream, stream_id, 12, close_price_id))) #rsi 12
        ret_inst.append(rsi(get_hist(stream, stream_id, 24, close_price_id))) #rsi 24
        
        #rsv
        arg = 9
        ret_inst.append(rsv(stream[stream_id][close_price_id], get_hist(stream, stream_id, arg, high_price_id), get_hist(stream, stream_id, arg, low_price_id))) #rsv 9

        arg = 18
        ret_inst.append(rsv(stream[stream_id][close_price_id], get_hist(stream, stream_id, arg, high_price_id), get_hist(stream, stream_id, arg, low_price_id))) #rsv 18

        arg = 27
        ret_inst.append(rsv(stream[stream_id][close_price_id], get_hist(stream, stream_id, arg, high_price_id), get_hist(stream, stream_id, arg, low_price_id))) #rsv 27

        #successive decrease days in one month
        ret_inst.append(dec_pred_len(get_hist(stream, stream_id, 30, close_price_id)))
    #print ret_inst
    
    return ret_inst

def stream_to_outfile(fn, sta_id, end_nonincl_id, stream, append_hist_len, if_label):
    fp = open(fn, 'w')
    tot = 0 #end_nonincl_id - sta_id
    pos_tot = 0
    for i in range(sta_id, end_nonincl_id):
        if i < 0:
            break
        tot += 1
        inst = get_instance(stream, i, append_hist_len, if_label)
        if inst[0] == '0':
            pos_tot += 1
        #fp.write(' '.join(inst) + '\n')
        fp.write(str(inst[0]))
        for j in range(1, len(inst)):
            fp.write(' %d:%f' % (j - 1, inst[j]))
        fp.write('#%s\n'% (stream[i][date_id]))
    print fn, ': TOT =', tot, 'POS =', pos_tot, 'POS_RATE =', pos_tot / (tot + 0.0)

    fp.close()


if __name__ != '__main__':
    exit(0)

IN_CSV = sys.argv[1]
OUT_DIR = sys.argv[2]
MY_STOCK_NAME = sys.argv[3]



stream = csv_to_stream(IN_CSV)

train_fn = OUT_DIR + '/' + MY_STOCK_NAME + '.train'
cv_fn = OUT_DIR + '/' + MY_STOCK_NAME + '.cv'
eval_fn = OUT_DIR + '/' + MY_STOCK_NAME + '.eval'

eval_sta_id = len(stream) - 1
cv_end_nonincl_id = len(stream) - pred_period
train_end_nonincl_id = int(math.floor((cv_end_nonincl_id - 1) * (1 - cv_rate)))

#print len(stream)
#print cv_end_nonincl_id
#print train_end_nonincl_id

#for i in range(10,21):
#    print stream[i]
#a = get_hist(stream, 103, 10, open_price_id)
#a = [1, -1, 3, 2, 5]
#print a
#print rsi(a)


#get_instance(stream, cv_end_nonincl_id - 1, 0, True)

stream_to_outfile(train_fn, 0, train_end_nonincl_id, stream, 0, True)
stream_to_outfile(cv_fn, train_end_nonincl_id, cv_end_nonincl_id, stream, 0, True)
stream_to_outfile(eval_fn, eval_sta_id, eval_sta_id + 1, stream, 0, False)

