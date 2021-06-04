#!/bin/sh


echo "Launching SGW-U2..."

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/sgwu2.log

tail -f /usr/local/var/log/open5gs/sgwu2.log &

open5gs-sgwud -c /usr/local/etc/open5gs/sgwu2.yaml
