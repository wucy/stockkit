#! /usr/bin/env python

import sys

import numpy
import xgboost




IN_PLAIN = sys.argv[1]
OUT_XGBFN = sys.argv[2]

data = xgboost.DMatrix(IN_PLAIN)

data.save_binary(OUT_XGBFN)


