#!/bin/bash

if [ ! -z $1 ]; then 
  proxy=$1
fi

python3 1.reg_presearch.py $proxy
