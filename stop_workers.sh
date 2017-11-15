#!/bin/bash

for i in ~/logs/*.pid; do
    pid=`cat $i`
    kill $pid
    kill -9 $pid
    echo "Killed $i: $pid"
done

rm -f ~/logs/*.pid
ps aux | grep cryptominisat5 | awk '{print $2}' | xargs kill
