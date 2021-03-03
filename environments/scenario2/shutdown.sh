#!/bin/bash

docker-compose -f docker-compose-5g-nsa-cpn.yml -f docker-compose-5g-nsa-upn.yml down
docker network rm cpn
docker network rm upn
docker network rm rfn
cd dovesnap
docker-compose -f docker-compose.yml -f docker-compose-standalone.yml down
cd ..
docker volume rm scenario2_mongodb_data
docker volume rm dovesnap_ovs-data
