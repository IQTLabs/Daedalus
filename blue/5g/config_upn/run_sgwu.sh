#!/bin/bash

host=$(hostname)
echo "Launching ${host}..."

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/${host}.log
tail -f /usr/local/var/log/open5gs/${host}.log &

open5gs-sgwud -c /usr/local/etc/open5gs/${host}.yaml
