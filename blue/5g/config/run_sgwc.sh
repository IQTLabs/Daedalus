#!/bin/sh


echo "Launching SGW-C..."

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/sgwc.log

tail -f /usr/local/var/log/open5gs/sgwc.log &

open5gs-sgwcd -c /usr/local/etc/open5gs/sgwc.yaml
