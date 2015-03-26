#! /usr/bin/python
import sys
import numpy as np
import xgboost as xgb

# label need to be 0 to num_class -1


train_fn = sys.argv[1]
cv_fn = sys.argv[2]


xg_train = xgb.DMatrix(train_fn)
xg_cv = xgb.DMatrix(cv_fn)
# setup parameters for xgboost
param = {}
# use softmax multi-class classification
param['objective'] = 'binary:logistic'

# scale weight of positive examples
param['eta'] = 1

param['max_depth'] = 4
param['silent'] = 1
param['nthread'] = 15
param['min_child_weight'] = 1.0
param['gamma'] = 1.0

param['save_period'] = 1

watchlist = [(xg_train,'train'), (xg_cv, 'cv')]
num_round = 10
bst = xgb.train(param, xg_train, num_round, watchlist);
# get prediction
#pred = bst.predict( xg_test );

#print ('predicting, classification error=%f' % (sum( int(pred[i]) != test_Y[i] for i in range(len(test_Y))) / float(len(test_Y)) ))

print str(param)

bst.save_model('xgb.model')


# do the same thing again, but output probabilities
#param['objective'] = 'multi:softprob'
#bst = xgb.train(param, xg_train, num_round, watchlist );
# Note: this convention has been changed since xgboost-unity
# get prediction, this is in 1D array, need reshape to (ndata, nclass)
#yprob = bst.predict( xg_test ).reshape( test_Y.shape[0], 6 )
#ylabel = np.argmax(yprob, axis=1)

#print ('predicting, classification error=%f' % (sum( int(ylabel[i]) != test_Y[i] for i in range(len(test_Y))) / float(len(test_Y)) ))
