#!/bin/bash

echo "building images..."

cd blue/5G/srsRAN || exit 1
docker build -t iqtlabs/srsran-base:latest -f Dockerfile.base .
docker build -t iqtlabs/srsran:latest -f Dockerfile.srs --build-arg SRS_VERSIONS=release_21_04 .
cd ../open5gs || exit 1
docker build -t iqtlabs/open5gs:latest .
cd ..

echo "starting dovesnap..."

sudo ip link add tpmirrorint type veth peer name tpmirror
sudo ip link set tpmirrorint up
sudo ip link set tpmirror up
mkdir -p /tmp/tpfaucet/etc/faucet
cp configs/faucet/faucet.yaml /tmp/tpfaucet/etc/faucet/
cp configs/faucet/acls.yaml /tmp/tpfaucet/etc/faucet/
curl -LJO https://github.com/iqtlabs/dovesnap/tarball/v1.0.1
tar -xvf IQTLabs-dovesnap-v1.0.1-0-gf8e4809.tar.gz
cd IQTLabs-dovesnap-f8e4809 || exit 1
MIRROR_BRIDGE_OUT='tpmirrorint' FAUCET_PREFIX='/tmp/tpfaucet' docker-compose -f docker-compose.yml -f docker-compose-standalone.yml up -d --build
cd ..

echo "creating networks..."

docker network create -o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 -o ovs.bridge.preallocate_ports=15 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d dovesnap -o ovs.bridge.vlan=26 -o ovs.bridge.dpid=0x620 -o ovs.bridge.mode=routed --subnet 192.168.26.0/24 --gateway 192.168.26.1 --ipam-opt com.docker.network.bridge.name=cpn -o ovs.bridge.nat_acl=protectcpn cpn

docker network create -o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 -o ovs.bridge.preallocate_ports=15 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d dovesnap -o ovs.bridge.vlan=27 -o ovs.bridge.dpid=0x630 -o ovs.bridge.mode=nat --subnet 192.168.27.0/24 --gateway 192.168.27.1 --ipam-opt com.docker.network.bridge.name=upn upn

docker network create -o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 -o ovs.bridge.preallocate_ports=15 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d dovesnap -o ovs.bridge.vlan=28 -o ovs.bridge.dpid=0x640 -o ovs.bridge.mode=flat --subnet 192.168.28.0/24 --gateway 192.168.28.1 --ipam-opt com.docker.network.bridge.name=rfn -o ovs.bridge.nat_acl=protectrfn rfn

docker network create -o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 -o ovs.bridge.preallocate_ports=15 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d dovesnap -o ovs.bridge.vlan=29 -o ovs.bridge.dpid=0x650 -o ovs.bridge.mode=routed --subnet 192.168.29.0/24 --gateway 192.168.29.1 --ipam-opt com.docker.network.bridge.name=ran -o ovs.bridge.nat_acl=protectran ran

echo "starting services..."
SMF='' docker-compose -f core/epc.yml -f core/upn.yml -f core/db.yml -f SIMULATED/srsran-enb.yml -f SIMULATED/srsran-ue.yml up -d --build
docker ue2 stop
docker ue3 stop
docker ue4 stop

echo "checking UE connectivity..."
sleep 180
docker logs ue
docker exec -it ue ping -I tun_srsue -c1 google.com
