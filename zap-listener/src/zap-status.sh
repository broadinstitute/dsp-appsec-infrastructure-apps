#!/bin/bash
# $1 - CodeDx API
# $2 - Project Name in CodeDx
# $3 - URL
# turn on bash's job control
set -m
# Start the primary process and put it in the background

while ! netstat -anp | grep 8008 | grep LISTEN ;
do
    if [ $counter == 300 ];
    then 
        exit 1;
    fi;
    echo "sleeping $counter";
    counter=$((counter+1));
    sleep 1s;
done
echo "done sleeping";