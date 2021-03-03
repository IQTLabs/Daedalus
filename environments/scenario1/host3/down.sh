#!/bin/bash

# stop all desktops
cd desktop
docker-compose -p 0 down
docker-compose -p 1 down
docker-compose -p 2 down
docker-compose -p 3 down
docker-compose -p 4 down
cd ..

# delete desktops network
docker network rm desktops

# stop dovesnap and ovs
cd dovesnap
docker-compose down
cd ..

# remove docker networks
docker network prune

# remove docker volumes
docker volume prune
