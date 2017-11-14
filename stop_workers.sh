#!/bin/bash

for i in ~/logs/*.pid; do
    pid=`cat $i`
    kill $pid
    kill -9 $pid
    echo "Killed $i: $pid"
done

rm ~/logs/*.pid
