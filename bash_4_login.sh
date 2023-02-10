#!/bin/bash

if [ ! -z $1 ]; then 
  email=$1
fi
if [ ! -z $2 ]; then 
  proxy=$2
fi

python3 4.login_email.py $email $proxy
