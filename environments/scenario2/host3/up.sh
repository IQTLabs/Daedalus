#!/bin/bash

SCENARIO=$1
COUNT=$2
echo "vlan: $VLAN" > scenario-"$SCENARIO"-cpn.txt
NAMES=($(cat hostnames.txt | sort -R | head -n $COUNT))
USERS=($(cat usernames.txt | sort -R | head -n $COUNT))
PASSWORDS=($(cat passwords.txt | sort -R | head -n $COUNT))
echo "hostnames: ${NAMES[@]}" >> scenario-"$SCENARIO"-cpn.txt
echo "usernames: ${USERS[@]}" >> scenario-"$SCENARIO"-cpn.txt
echo "passwords: ${PASSWORDS[@]}" >> scenario-"$SCENARIO"-cpn.txt

cd dovesnap
MIRROR_BRIDGE_OUT=enp4s0 MIRROR_BRIDGE_IN=enp3s0 FAUCETCONFRPC_IP=192.168.199.1 STACK_OFCONTROLLERS=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 docker-compose -f docker-compose.yml up -d --build
cd ..

#docker network create -o ovs.bridge.dpid=0x600 -o ovs.bridge.mode=nat --subnet 192.168.26.0/24 --gateway 192.168.26.1 --ipam-opt com.docker.network.bridge.name=cpn -o ovs.bridge.nat_acl=protectcpn -o ovs.bridge.add_ports=VLAN26/1 -o ovs.bridge.vlan=26 -o ovs.bridge.controller=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 -o ovs.bridge.mtu=9000 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d ovs cpn

docker network create -o ovs.bridge.dpid=0x600 -o ovs.bridge.mode=flat --subnet 192.168.26.0/24 --gateway 192.168.26.1 -o ovs.bridge.add_ports=VLAN26/1 -o ovs.bridge.nat_acl=protectcpn -o ovs.bridge.vlan=26 -o ovs.bridge.dhcp=false -o ovs.bridge.controller=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 --internal -d ovs cpn

docker network create -o ovs.bridge.dpid=0x610 -o ovs.bridge.mode=flat -o ovs.bridge.add_ports=VLAN29/1 -o ovs.bridge.vlan=29 -o ovs.bridge.dhcp=true -o ovs.bridge.controller=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 -o ovs.bridge.add_copro_ports=enp2s0/999 --ipam-driver null --internal -d ovs desktops

cd mongoloader && docker build -t mongoloader . && cd ..

docker build -t open5gs . && docker-compose -f docker-compose-5g-nsa-cpn.yml up -d --build

# start entrypoint desktop
VNC=$(apg -n 1)
echo "VNC external password: $VNC" >> scenario-"$SCENARIO"-cpn.txt
cd desktop
SYSTEM_USER=${USERS[0]} USER_PW=${PASSWORDS[0]} CONTAINER_NAME=${NAMES[0]} VNC_PASSWORD=$VNC docker-compose -p 0 up -d --build
cd ..
cd dba
SYSTEM_USER=${USERS[1]} USER_PW=${PASSWORDS[1]} CONTAINER_NAME=${NAMES[1]} VNC_PASSWORD=$VNC docker-compose -p 1 up -d --build
cd ..
echo "started desktop entrypoint... hostname: ${NAMES[0]} username: ${USERS[0]} password: ${PASSWORDS[0]} vnc: $VNC" >> scenario-"$SCENARIO"-cpn.txt
echo "started dba... hostname: ${NAMES[1]} username: ${USERS[1]} password: ${PASSWORDS[1]} vnc: $VNC" >> scenario-"$SCENARIO"-cpn.txt
