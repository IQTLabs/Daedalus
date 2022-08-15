#!/bin/bash

set -e

DSVER=v1.1.1
export FAUCET_PREFIX='/tmp/tpfaucet'
export MIRROR_BRIDGE_OUT='tpmirrorint'

echo "building images..."

cd blue/5G/daedalus/5G/srsRAN && \
    docker build -t iqtlabs/srsran:latest -f Dockerfile . && \
    cd .. || exit 1
cd open5gs && docker build -t iqtlabs/open5gs:latest . && cd .. || exit 1
cd UERANSIM && docker build -t iqtlabs/ueransim:latest . && cd .. || exit 1

echo "starting dovesnap..."

docker network prune -f && docker system prune -f && docker volume prune -f
sudo ip link add tpmirrorint type veth peer name tpmirror || true
sudo ip link set tpmirrorint up
sudo ip link set tpmirror up
sudo rm -rf ${FAUCET_PREFIX}
mkdir -p ${FAUCET_PREFIX}/etc/faucet
cp configs/faucet/faucet.yaml ${FAUCET_PREFIX}/etc/faucet/
cp configs/faucet/acls.yaml ${FAUCET_PREFIX}/etc/faucet/
rm -rf IQTLabs-dovesnap* && curl -LJ https://github.com/iqtlabs/dovesnap/tarball/${DSVER} | tar zxvf -
cd IQTLabs-dovesnap*/
docker-compose -f docker-compose.yml -f docker-compose-standalone.yml down -v
docker-compose -f docker-compose.yml -f docker-compose-standalone.yml up -d --build
cd ..

echo "creating networks..."

docker network create -o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 -o ovs.bridge.preallocate_ports=15 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d dovesnap -o ovs.bridge.vlan=26 -o ovs.bridge.dpid=0x620 -o ovs.bridge.mode=routed --subnet 192.168.26.0/24 --gateway 192.168.26.1 --ipam-opt com.docker.network.bridge.name=cpn -o ovs.bridge.nat_acl=protectcpn cpn

docker network create -o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 -o ovs.bridge.preallocate_ports=15 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d dovesnap -o ovs.bridge.vlan=27 -o ovs.bridge.dpid=0x630 -o ovs.bridge.mode=nat --subnet 192.168.27.0/24 --gateway 192.168.27.1 --ipam-opt com.docker.network.bridge.name=upn upn

docker network create -o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 -o ovs.bridge.preallocate_ports=15 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d dovesnap -o ovs.bridge.vlan=28 -o ovs.bridge.dpid=0x640 -o ovs.bridge.mode=flat --subnet 192.168.28.0/24 --gateway 192.168.28.1 --ipam-opt com.docker.network.bridge.name=rfn -o ovs.bridge.nat_acl=protectrfn rfn

docker network create -o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 -o ovs.bridge.preallocate_ports=15 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d dovesnap -o ovs.bridge.vlan=29 -o ovs.bridge.dpid=0x650 -o ovs.bridge.mode=routed --subnet 192.168.29.0/24 --gateway 192.168.29.1 --ipam-opt com.docker.network.bridge.name=ran -o ovs.bridge.nat_acl=protectran ran
