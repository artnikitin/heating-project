#!/bin/bash
_file="$1"
[ $# -eq 0 ] && { echo "Usage: $0 filename"; exit 1; }
[ ! -f "$_file" ] && { echo "Error: $0 file not found."; exit 2; }

for i in 1 2 3 4
do
    if [ $i == 4 ]
    then
        truncate -s 0 "$_file"
    else
        if [ -s "$_file" ]
        then
            echo "$_file has some data."
                echo "Attempt $i: " >> /path/to/log.txt
                # do something as file has data
                cd /path/to/project && /path/to/interpreter/bin/python3.6 /path/to/forecast.py >> /path/to/log.txt
        else
            echo "$_file is empty." >> /path/to/log.txt
                # do something as file is empty
                break
        fi
    fi
done