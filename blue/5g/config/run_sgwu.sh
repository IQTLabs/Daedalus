#!/bin/sh


echo "Launching SGW-U..."

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/sgwu.log

tail -f /usr/local/var/log/open5gs/sgwu.log &

open5gs-sgwud -c /usr/local/etc/open5gs/sgwu.yaml
