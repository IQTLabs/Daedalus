#!/bin/sh

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/udm.log

tail -f /usr/local/var/log/open5gs/udm.log &

open5gs-udmd -c /usr/local/etc/open5gs/udm.yaml
