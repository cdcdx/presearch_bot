#!/bin/bash

if [ ! -z $1 ]; then 
  file=$1
fi

python3 3.fast_lunch.py $file
