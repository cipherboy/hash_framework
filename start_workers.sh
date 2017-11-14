#!/bin/bash

num_process=`cat /proc/cpuinfo | grep 'processor' | wc -l`
min_port=5000
max_port=$((min_port + num_process))

mkdir -p ~/logs

for port in `seq $min_port $max_port`; do
    echo "Starting..."
    python3 -m hash_framework.workers $port 2> ~/logs/worker-$port-err.log >~/logs/worker-$port.log &
    pid="$!"
    echo "PID: $pid"
    echo "$pid" > ~/logs/worker-$port.pid
done
