#!/bin/bash

VLAN=$1
SCENARIO=$2
COUNT=$3
echo "vlan: $VLAN" > scenario-"$SCENARIO"-desktops.txt
NAMES=($(cat hostnames.txt | sort -R | head -n $COUNT))
USERS=($(cat usernames.txt | sort -R | head -n $COUNT))
PASSWORDS=($(cat passwords.txt | sort -R | head -n $COUNT))
echo "hostnames: ${NAMES[@]}" >> scenario-"$SCENARIO"-desktops.txt
echo "usernames: ${USERS[@]}" >> scenario-"$SCENARIO"-desktops.txt
echo "passwords: ${PASSWORDS[@]}" >> scenario-"$SCENARIO"-desktops.txt

# start dovesnap and ovs
cd dovesnap
MIRROR_BRIDGE_OUT=enp4s0 MIRROR_BRIDGE_IN=enp3s0 FAUCETCONFRPC_IP=192.168.199.1 STACK_OFCONTROLLERS=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 docker-compose -f docker-compose.yml up -d --build
cd ..

# create desktop network
docker network create -o ovs.bridge.dpid=0x500 -o ovs.bridge.mode=flat -o ovs.bridge.add_ports=VLAN$VLAN/1/protectmesrc -o ovs.bridge.vlan=$VLAN -o ovs.bridge.dhcp=true -o ovs.bridge.controller=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 -o ovs.bridge.add_copro_ports=enp2s0/999 --ipam-driver null --internal -d ovs desktops

# start entrypoint desktop
VNC=$(apg -n 1)
echo "VNC external password: $VNC" >> scenario-"$SCENARIO"-desktops.txt
cd desktop
SYSTEM_USER=${USERS[0]} USER_PW=${PASSWORDS[0]} CONTAINER_NAME=${NAMES[0]} VNC_PASSWORD=$VNC docker-compose -p 0 up -d --build

# start 4 desktops
SYSTEM_USER=${USERS[1]} USER_PW=${PASSWORDS[1]} CONTAINER_NAME=${NAMES[1]} VNC_PASSWORD=$VNC docker-compose -p 1 up -d --build
SYSTEM_USER=${USERS[2]} USER_PW=${PASSWORDS[2]} CONTAINER_NAME=${NAMES[2]} VNC_PASSWORD=$VNC docker-compose -p 2 up -d --build
SYSTEM_USER=${USERS[3]} USER_PW=${PASSWORDS[3]} CONTAINER_NAME=${NAMES[3]} VNC_PASSWORD=$VNC docker-compose -p 3 up -d --build
SYSTEM_USER=${USERS[4]} USER_PW=${PASSWORDS[4]} CONTAINER_NAME=${NAMES[4]} VNC_PASSWORD=$VNC docker-compose -p 4 up -d --build
cd ..
echo "started desktop entrypoint... hostname: ${NAMES[0]} username: ${USERS[0]} password: ${PASSWORDS[0]} vnc: $VNC" >> scenario-"$SCENARIO"-desktops.txt
echo "started desktop 1... hostname: ${NAMES[1]} username: ${USERS[1]} password: ${PASSWORDS[1]} vnc: $VNC" >> scenario-"$SCENARIO"-desktops.txt
echo "started desktop 2... hostname: ${NAMES[2]} username: ${USERS[2]} password: ${PASSWORDS[2]} vnc: $VNC" >> scenario-"$SCENARIO"-desktops.txt
echo "started desktop 3... hostname: ${NAMES[3]} username: ${USERS[3]} password: ${PASSWORDS[3]} vnc: $VNC" >> scenario-"$SCENARIO"-desktops.txt
echo "started desktop 4... hostname: ${NAMES[4]} username: ${USERS[4]} password: ${PASSWORDS[4]} vnc: $VNC" >> scenario-"$SCENARIO"-desktops.txt
