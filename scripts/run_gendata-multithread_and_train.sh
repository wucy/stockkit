#! /bin/bash

#./scripts/gen_dataset.py data/tdx/ data/acc

time scripts/gen_dataset-multithread.py data/tdx data/acc

./scripts/train.py data/acc/init/train.xgb data/acc/init/cv.xgb

