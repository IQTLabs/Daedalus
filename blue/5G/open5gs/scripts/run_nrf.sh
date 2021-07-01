#!/bin/sh

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/nrf.log

tail -f /usr/local/var/log/open5gs/nrf.log &

open5gs-nrfd -c /usr/local/etc/open5gs/nrf.yaml
