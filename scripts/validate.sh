#!/usr/bin/env bash
pip install --upgrade sgvalidator

if [ $# -eq 1 ]
then
   python validate.py $1
elif [ $# -gt 1 ]
then
   python validate.py $1 $2
fi