#!/bin/bash

num_process=`cat /proc/cpuinfo | grep 'processor' | wc -l`

bash ./stop_workers.sh
mkdir -p ~/logs
rm -rf ~/models ~/kernel_cache
mkdir -p ~/models ~/kernel_cache ~/results

for proc in `seq 1 $num_process`; do
    echo "Starting..."
    python3 -m hash_framework.workers $@ 2> ~/logs/worker-$proc-err.log >~/logs/worker-$proc.log &
    pid="$!"
    echo "PID: $pid"
    echo "$pid" > ~/logs/worker-$proc.pid
done
