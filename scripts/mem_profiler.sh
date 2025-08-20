#!/bin/bash

PID_TO_MONITOR=$1
MEM_LOG=$2

> "$MEM_LOG"

while ps -p "$PID_TO_MONITOR" > /dev/null; do
    MEM_USAGE=$(ps -p "$PID_TO_MONITOR" -o rss=)

    echo "$(date +'%Y-%m-%d %H:%M:%S') | Memória (kB): $MEM_USAGE" >> "$MEM_LOG"

    sleep 10
done
