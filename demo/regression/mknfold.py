#!/usr/bin/python
import sys
import random

if len(sys.argv) < 2:
    print ('Usage:<filename> <k> [nfold = 5]')
    exit(0)

random.seed( 10 )

k = int( sys.argv[2] )
nfold = int( sys.argv[3] ) if len(sys.argv) > 3 else 5
with open( sys.argv[1], 'r' ) as fi:
    ftr = open(f'{sys.argv[1]}.train', 'w')
    fte = open(f'{sys.argv[1]}.test', 'w')
    for l in fi:
        if random.randint( 1 , nfold ) == k:
            fte.write( l )
        else:
            ftr.write( l )

ftr.close()
fte.close()

