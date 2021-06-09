#!/bin/bash

docker-compose -f docker-compose-5g-nsa.yml down
docker volume rm scenario2_mongodb_data
