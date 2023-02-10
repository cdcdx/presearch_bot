#!/bin/bash

if [ ! -z $1 ]; then 
  file=$1
fi
if [ ! -z $2 ]; then 
  proxy=$2
fi

python3 3.fast_lunch.py $file $proxy
