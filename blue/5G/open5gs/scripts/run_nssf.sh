#!/bin/sh

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/nssf.log

tail -f /usr/local/var/log/open5gs/nssf.log &

open5gs-nssfd -c /usr/local/etc/open5gs/nssf.yaml
