#!/bin/bash

set -e

UETEST=$(dirname "$0")/uetuncheck.sh
UETEST=$(realpath "${UETEST}")

echo "starting services..."
cd blue/5G/daedalus/5G
CLI=('-f' 'core/epc.yml' '-f' 'core/upn.yml' '-f' 'core/db.yml' '-f' 'core/core.yml' '-f' 'SIMULATED/ueransim-gnb.yml' '-f' 'SIMULATED/ueransim-ue.yml')

SMF='core' docker-compose "${CLI[@]}" down -v
SMF='core' docker-compose "${CLI[@]}" up -d --build

${UETEST} ue1 uesimtun0

CMD='core' docker-compose "${CLI[@]}" down -v
