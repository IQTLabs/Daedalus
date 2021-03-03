#!/bin/bash

# stop vuln tomcat

# stop all other servers
cd server
docker-compose -p 0 down
docker-compose -p 1 down
docker-compose -p 2 down
docker-compose -p 3 down
docker-compose -p 4 down
cd ..

# stop nfs

# delete servers network
docker network rm servers

# stop dovesnap and ovs
cd dovesnap
docker-compose down
cd ..

# remove docker networks
docker network prune

# remove docker volumes
docker volume prune

sudo service docker restart
