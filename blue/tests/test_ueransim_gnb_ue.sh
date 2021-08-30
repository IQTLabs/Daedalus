#!/bin/bash

echo "starting services..."
cd blue/5G || exit 1
SMF='core' docker-compose -f core/epc.yml -f core/upn.yml -f core/db.yml -f core/core.yml -f SIMULATED/ueransim-gnb.yml -f SIMULATED/ueransim-ue.yml up -d --build

echo "checking UE connectivity..."
sleep 300
docker logs ue1
docker exec ue1 ping -I uesimtun0 -c1 google.com
docker-compose -f core/epc.yml -f core/upn.yml -f core/db.yml -f core/core.yml -f SIMULATED/ueransim-gnb.yml -f SIMULATED/ueransim-ue.yml down
