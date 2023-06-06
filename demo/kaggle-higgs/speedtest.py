#!/usr/bin/python
# this is the example script to use xgboost to train
import numpy as np
import xgboost as xgb
from sklearn.ensemble import GradientBoostingClassifier
import time
test_size = 550000

# path to where the data lies
dpath = 'data'

# load in training data, directly use numpy
dtrain = np.loadtxt(
    f'{dpath}/training.csv',
    delimiter=',',
    skiprows=1,
    converters={32: lambda x: int(x == 's')},
)
print ('finish loading from csv ')

label  = dtrain[:,32]
data   = dtrain[:,1:31]
# rescale weight to make it same as test set
weight = dtrain[:,31] * float(test_size) / len(label)

sum_wpos = sum( weight[i] for i in range(len(label)) if label[i] == 1.0  )
sum_wneg = sum( weight[i] for i in range(len(label)) if label[i] == 0.0  )

# print weight statistics
print ('weight statistics: wpos=%g, wneg=%g, ratio=%g' % ( sum_wpos, sum_wneg, sum_wneg/sum_wpos ))

# construct xgboost.DMatrix from numpy array, treat -999.0 as missing value
xgmat = xgb.DMatrix( data, label=label, missing = -999.0, weight=weight )

# setup parameters for xgboost
param = {
    'objective': 'binary:logitraw',
    'scale_pos_weight': sum_wneg / sum_wpos,
    'bst:eta': 0.1,
    'bst:max_depth': 6,
    'eval_metric': 'auc',
    'nthread': 4,
}
plst = param.items()+[('eval_metric', 'ams@0.15')]

watchlist = [ (xgmat,'train') ]
# boost 10 trees
num_round = 10
print ('loading data end, start to boost trees')
print ("training GBM from sklearn")
tmp = time.time()
gbm = GradientBoostingClassifier(n_estimators=num_round, max_depth=6, verbose=2)
gbm.fit(data, label)
print(f"sklearn.GBM costs: {str(time.time() - tmp)} seconds")
#raw_input()
print ("training xgboost")
threads = [1, 2, 4, 16]
for i in threads:
    param['nthread'] = i
    tmp = time.time()
    plst = param.items()+[('eval_metric', 'ams@0.15')]
    bst = xgb.train( plst, xgmat, num_round, watchlist );
    print ("XGBoost with %d thread costs: %s seconds" % (i, str(time.time() - tmp)))

print ('finish training')
