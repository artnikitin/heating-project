#!/bin/bash
truncate -s 0 /path/to/log.txt
cd /path/to/project && /path/to/interpreter/bin/python3.6 /path/to/forecast.py >> /path/to/log.txt
dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "Executed forecast.py successfully on $dt" >> /path/to/log.txt

./misfired.sh misfired.txt