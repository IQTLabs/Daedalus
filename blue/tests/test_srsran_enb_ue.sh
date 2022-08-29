#!/bin/bash

set -e

UETEST=$(dirname "$0")/uetuncheck.sh
UETEST=$(realpath "${UETEST}")

echo "starting services..."
cd blue/5G/daedalus/5G
CLI=('-f' 'core/epc.yml' '-f' 'core/upn.yml' '-f' 'core/db.yml' '-f' 'SIMULATED/srsran-enb.yml' '-f' 'SIMULATED/srsran-ue.yml')

SMF='' docker-compose "${CLI[@]}" down -v
SMF='' docker-compose "${CLI[@]}" up -d --build

${UETEST} ue tun_srsue

docker-compose "${CLI[@]}" down -v
