#!/bin/bash

UETEST=$(dirname "$0")/uetuncheck.sh
UETEST=$(realpath "${UETEST}")

echo "starting services..."
cd blue/5G || exit 1
SMF='core' docker-compose -f core/epc.yml -f core/upn.yml -f core/db.yml -f core/core.yml -f SIMULATED/ueransim-gnb.yml -f SIMULATED/ueransim-ue.yml up -d --build

${UETEST} ue1 uesimtun0

docker-compose -f core/epc.yml -f core/upn.yml -f core/db.yml -f core/core.yml -f SIMULATED/ueransim-gnb.yml -f SIMULATED/ueransim-ue.yml down
