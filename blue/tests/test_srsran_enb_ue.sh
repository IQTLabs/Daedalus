#!/bin/bash

set -e

UETEST=$(dirname "$0")/uetuncheck.sh
UETEST=$(realpath "${UETEST}")

echo "starting services..."
cd blue/5G || exit 1
SMF='' docker-compose -f core/epc.yml -f core/upn.yml -f core/db.yml -f SIMULATED/srsran-enb.yml -f SIMULATED/srsran-ue.yml up -d --build

${UETEST} ue tun_srsue

docker-compose -f core/epc.yml -f core/upn.yml -f core/db.yml -f SIMULATED/srsran-enb.yml -f SIMULATED/srsran-ue.yml down
