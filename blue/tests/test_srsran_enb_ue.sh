#!/bin/bash

echo "starting services..."
cd blue/5G || exit 1
SMF='' docker-compose -f core/epc.yml -f core/upn.yml -f core/db.yml -f SIMULATED/srsran-enb.yml -f SIMULATED/srsran-ue.yml up -d --build
docker stop ue2
docker stop ue3
docker stop ue4

echo "checking UE connectivity..."
sleep 300
docker logs ue
docker exec ue ping -I tun_srsue -c1 google.com
docker-compose -f core/epc.yml -f core/upn.yml -f core/db.yml -f SIMULATED/srsran-enb.yml -f SIMULATED/srsran-ue.yml down
