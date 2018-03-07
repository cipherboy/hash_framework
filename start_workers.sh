#!/bin/bash

num_process=`cat /proc/cpuinfo | grep 'processor' | wc -l`

bash ./stop_workers.sh
mkdir -p ~/logs
rm -rf ~/models ~/kernel_cache
mkdir -p ~/models ~/kernel_cache ~/results

for port in `seq $min_port $max_port`; do
    echo "Starting..."
    python3 -m hash_framework.workers $@ 2> ~/logs/worker-$port-err.log >~/logs/worker-$port.log &
    pid="$!"
    echo "PID: $pid"
    echo "$pid" > ~/logs/worker-$port.pid
done
