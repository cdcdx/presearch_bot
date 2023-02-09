#!/bin/bash

if [ -z $1 ]; then 
  email="cdcdx888@gmail.com"
else
  email=$1
fi

python3 4.login_email.py $email
