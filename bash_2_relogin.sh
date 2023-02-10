#!/bin/bash

if [ ! -z $1 ]; then 
  proxy=$1
fi

python3 2.relogin.py $proxy
