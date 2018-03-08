#!/bin/bash

echo "Killing scheduler..."
pid=`cat ~/logs/scheduler.pid`
kill $pid
kill -9 $pid
rm -f ~/logs/scheduler.pid

echo "Killing manager..."
pid=`cat ~/logs/manager.pid`
kill $pid
kill -9 $pid
rm -f ~/logs/manager.pid
