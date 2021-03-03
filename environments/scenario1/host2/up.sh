#!/bin/bash

VLAN=$1
SCENARIO=$2
COUNT=$3
echo "vlan: $VLAN" > scenario-"$SCENARIO"-servers.txt
NAMES=($(cat hostnames.txt | sort -R | head -n $COUNT))
USERS=($(cat usernames.txt | sort -R | head -n $COUNT))
PASSWORDS=($(cat passwords.txt | sort -R | head -n $COUNT))
echo "hostnames: ${NAMES[@]}" >> scenario-"$SCENARIO"-servers.txt
echo "usernames: ${USERS[@]}" >> scenario-"$SCENARIO"-servers.txt
echo "passwords: ${PASSWORDS[@]}" >> scenario-"$SCENARIO"-servers.txt

# start dovesnap and ovs
cd dovesnap
MIRROR_BRIDGE_OUT=enp4s0 MIRROR_BRIDGE_IN=enp3s0 FAUCETCONFRPC_IP=192.168.199.1 STACK_OFCONTROLLERS=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 docker-compose -f docker-compose.yml up -d --build
cd ..

# create servers network
docker network create -o ovs.bridge.dpid=0x600 -o ovs.bridge.mode=flat -o ovs.bridge.add_ports=VLAN$VLAN/1/noinetsrc -o ovs.bridge.vlan=$VLAN -o ovs.bridge.dhcp=true -o ovs.bridge.controller=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 -o ovs.bridge.add_copro_ports=enp2s0/999 --ipam-driver null --internal -d ovs servers

# start nfs server
cd nfs_server
docker build -t erichough/nfs-server .
cd ..
docker run --network=servers -l "dovesnap.faucet.mirror=true" -v /nfs:/share --cap-add SYS_ADMIN --name ${NAMES[0]} --hostname ${NAMES[0]} -e NFS_EXPORT_0='/share *(ro,no_subtree_check,fsid=0)' --security-opt apparmor=erichough-nfs -d -e NFS_VERSION=4.2 -e NFS_DISABLE_VERSION_3=1 erichough/nfs-server
docker exec -it ${NAMES[0]} adduser -D -u 1000 ${USERS[0]}
docker exec -it ${NAMES[0]} passwd -u ${USERS[0]}
docker exec -it -e USERNAME=${USERS[0]} -e PASSWORD=${PASSWORDS[0]} ${NAMES[0]} bash -c 'echo "$USERNAME:$PASSWORD" | chpasswd'
docker exec -it ${NAMES[0]} adduser ${USERS[0]} wheel
echo "started nfs server... hostname: ${NAMES[0]} username: ${USERS[0]} password: ${PASSWORDS[0]}" >> scenario-"$SCENARIO"-servers.txt

# start tomcat server
cd tomcat_vuln_server
sed "s/tomcatpass/${PASSWORDS[1]}/g" tomcat-users.xml.orig > tomcat-users.xml
CONTAINER_NAME=${NAMES[1]} docker-compose up -d --build
cd ..
docker exec -it tomcat_vuln_server_tomcat_1 useradd -m ${USERS[1]}
docker exec -it -e USERNAME=${USERS[1]} -e PASSWORD=${PASSWORDS[1]} tomcat_vuln_server_tomcat_1 bash -c 'echo "$USERNAME:$PASSWORD" | chpasswd'
docker exec -it tomcat_vuln_server_tomcat_1 adduser ${USERS[1]} sudo
echo "started vulnerable tomcat server... hostname: ${NAMES[1]} username: ${USERS[1]} password: ${PASSWORDS[1]}" >> scenario-"$SCENARIO"-servers.txt
echo "tomcat server manager... username: tomcat password: ${PASSWORDS[1]}" >> scenario-"$SCENARIO"-servers.txt

# start 6 servers

# start 1 ssh servers
cd ssh_server
docker build -t panubo/sshd .
cd ..
docker run --network=servers -l "dovesnap.faucet.mirror=true" --cap-add SYS_ADMIN --name ${NAMES[2]} --hostname ${NAMES[2]} --security-opt apparmor=erichough-nfs -d -e SSH_USERS=${USERS[2]}:1000:1000 -e SSH_ENABLE_PASSWORD_AUTH=true panubo/sshd
sleep 10
docker exec -it ${NAMES[2]} passwd -u ${USERS[2]}
docker exec -it -e USERNAME=${USERS[2]} -e PASSWORD=${PASSWORDS[2]} ${NAMES[2]} bash -c 'echo "$USERNAME:$PASSWORD" | chpasswd'
docker exec -it ${NAMES[2]} adduser ${USERS[2]} wheel
echo "started panubo/sshd server 1... hostname: ${NAMES[2]} username: ${USERS[2]} password: ${PASSWORDS[2]}" >> scenario-"$SCENARIO"-servers.txt

# start 1 ssh servers
cd ssh_server2
docker build -t maltyxx/sshd .
cd ..
docker run --network=servers -l "dovesnap.faucet.mirror=true" --cap-add SYS_ADMIN --name ${NAMES[4]} --hostname ${NAMES[4]} --security-opt apparmor=erichough-nfs -d maltyxx/sshd ${USERS[4]}:${PASSWORDS[4]}:1001:1001
sleep 10
docker exec -it ${NAMES[4]} adduser ${USERS[4]} sudo
echo "started maltyxx/sshd server... hostname: ${NAMES[4]} username: ${USERS[4]} password: ${PASSWORDS[4]}" >> scenario-"$SCENARIO"-servers.txt

# start 1 httpd servers
cd httpd_server
docker build -t httpd .
cd ..
docker run --network=servers -l "dovesnap.faucet.mirror=true" --cap-add SYS_ADMIN --name ${NAMES[6]} --hostname ${NAMES[6]} --security-opt apparmor=erichough-nfs -d httpd
docker exec -it ${NAMES[6]} useradd -m ${USERS[6]}
docker exec -it -e USERNAME=${USERS[6]} -e PASSWORD=${PASSWORDS[5]} ${NAMES[6]} bash -c 'echo "$USERNAME:$PASSWORD" | chpasswd'
docker exec -it ${NAMES[6]} adduser ${USERS[6]} sudo
echo "started httpd server... hostname: ${NAMES[6]} username: ${USERS[6]} password: ${PASSWORDS[6]}" >> scenario-"$SCENARIO"-servers.txt

# start 2 tomcat servers
cd tomcat_server_extra
docker build -t tomcat:9.0 .
cd ..
docker run --network=servers -l "dovesnap.faucet.mirror=true" --cap-add SYS_ADMIN --name ${NAMES[8]} --hostname ${NAMES[8]} --security-opt apparmor=erichough-nfs -d tomcat:9.0
docker exec -it ${NAMES[8]} useradd -m ${USERS[8]}
docker exec -it -e USERNAME=${USERS[8]} -e PASSWORD=${PASSWORDS[8]} ${NAMES[8]} bash -c 'echo "$USERNAME:$PASSWORD" | chpasswd'
docker exec -it ${NAMES[8]} adduser ${USERS[8]} sudo
echo "started tomcat:9.0 server... hostname: ${NAMES[8]} username: ${USERS[8]} password: ${PASSWORDS[8]}" >> scenario-"$SCENARIO"-servers.txt
docker run --network=servers -l "dovesnap.faucet.mirror=true" --cap-add SYS_ADMIN --name ${NAMES[9]} --hostname ${NAMES[9]} --security-opt apparmor=erichough-nfs -d tomcat:9.0
docker exec -it ${NAMES[9]} useradd -m ${USERS[9]}
docker exec -it -e USERNAME=${USERS[9]} -e PASSWORD=${PASSWORDS[9]} ${NAMES[9]} bash -c 'echo "$USERNAME:$PASSWORD" | chpasswd'
docker exec -it ${NAMES[9]} adduser ${USERS[9]} sudo
echo "started tomcat:9.0 server 2... hostname: ${NAMES[9]} username: ${USERS[9]} password: ${PASSWORDS[9]}" >> scenario-"$SCENARIO"-servers.txt

# start 1 nfs servers
cd nfs_server_extra
docker build -t gists/nfs-server .
cd ..
docker run --network=servers -l "dovesnap.faucet.mirror=true" --privileged -e "NFS_DOMAIN=0.0.0.0" --name ${NAMES[11]} --hostname ${NAMES[11]}  -v /home/clewis/foo:/nfs-share -d gists/nfs-server
docker exec -it ${NAMES[11]} adduser -D -u 1000 ${USERS[11]}
docker exec -it ${NAMES[11]} passwd -u ${USERS[11]}
docker exec -it -e USERNAME=${USERS[11]} -e PASSWORD=${PASSWORDS[11]} ${NAMES[11]} bash -c 'echo "$USERNAME:$PASSWORD" | chpasswd'
docker exec -it ${NAMES[11]} adduser ${USERS[11]} wheel
echo "started gists/nfs-server server... hostname: ${NAMES[11]} username: ${USERS[11]} password: ${PASSWORDS[11]}" >> scenario-"$SCENARIO"-servers.txt

exit
