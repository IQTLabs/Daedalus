#!/bin/bash


PRB=50
BLADERF=0
BLADERF_EARFCN=3400
ETTUS=0
ETTUS_EARFCN=1800
LIMESDR=0
LIMESDR_EARFCN=900
VUE=1
SRS_VERSION="release_21_04"
RAN=0
CPN=1
UPN=1
GNB=0
RFN=0

export PRB

print_help()
{
	# Display help
	echo "5G startup script for running various 5G combinations automatically"
	echo
	echo "./startup.sh [-behlVCU]"
	echo "./startup.sh [-B|E|L] <EARAFCN>"
        echo
	echo "Options:"
	echo
	echo "-b     run bladeRF eNB"
	echo "-B <n> bladeRF EARFCN"
        echo "-e:    run Ettus eNB"
        echo "-E <n> ettus EARFCN"
	echo "-g     run UERANSIM gNB and UEs"
	echo "-h     print this help"
        echo "-l     run LimeSDR eNB"
        echo "-L <n> LimeSDR EARFCN"
        echo "-V     DO NOT run virtual eNB and UEs."
        echo "-C     DO NOT run the CPN"
        echo "-U     DO NOT run the UPN"
	echo
        echo "For example, to run bladeRF only:"
        echo "./startup.sh -bV"
	echo
        echo "No arguments will run virtual eNB and UEs by default"
	echo
}

while getopts "bB:eE:lL:VCUgh" o; do
    case "${o}" in
        b)
            BLADERF=1
            RAN=1
            ;;
        B)
            BLADERF_EARFCN=${OPTARG}
            ;;
        e)
            ETTUS=1
            RAN=1
            ;;
        E)
            ETTUS_EARFCN=${OPTARG}
            ;;
        h)
            print_help
	    exit 0
	    ;;
        l)
            LIMESDR=1
            RAN=1
            ;;
	g)
            GNB=1
            RAN=1
	    RFN=1
	    ;;
        L)
            LIMESDR_EARFCN=${OPTARG}
            ;;
        V)
            VUE=0
	    ;;
	C)
	    CPN=0
            ;;
	U)
	    UPN=0
            ;;
    esac
done
shift $((OPTIND-1))

if [[ "$VUE" -eq 1 ]] ; then RAN=1 ; RFN=1 ; fi

echo start bladeRF: $BLADERF
echo start ettus: $ETTUS
echo start limesdr: $LIMESDR
echo start virtual UEs/eNB: $VUE
echo start CPN: $CPN
echo start UPN: $UPN
echo start GNB: $GNB
echo start RAN: $RAN
echo start RFN: $RFN

if [[ "$LIMESDR" -eq 1 ]]; then
	SRS_VERSION="release_19_12"
fi

echo building srsRAN version: $SRS_VERSION

cd srsRAN && docker build -f Dockerfile.base -t srsran:base . && docker build --build-arg SRS_VERSION="$SRS_VERSION" -f Dockerfile.srs -t srsran . && cd .. || exit 1
cd open5gs && docker build -t open5gs . && cd .. || exit 1
cd UERANSIM && docker build -t ueransim . && cd .. || exit 1

sudo ip link add tpmirrorint type veth peer name tpmirror
sudo ip link set tpmirrorint up || exit 1
sudo ip link set tpmirror up || exit 1

TPFAUCETPREFIX=/tmp/tpfaucet
sudo rm -rf $TPFAUCETPREFIX && mkdir -p $TPFAUCETPREFIX/etc/faucet && cp configs/faucet/* $TPFAUCETPREFIX/etc/faucet || exit 1

git clone https://github.com/iqtlabs/dovesnap || echo "... ok."
cd dovesnap && git checkout main && git pull && git fetch --all --tags && git checkout $(git describe --tags --abbrev=0) && MIRROR_BRIDGE_OUT=tpmirrorint FAUCET_PREFIX=$TPFAUCETPREFIX docker-compose -f docker-compose.yml -f docker-compose-standalone.yml up -d && cd .. || exit 1

DOVESNAPOPTS="-o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 --ipam-opt com.docker.network.driver.mtu=9000 --internal"
DOCKERFILES=""

if [[ "$CPN" -eq 1 ]] ; then
        docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=26 -o ovs.bridge.dpid=0x620 -o ovs.bridge.mode=routed --subnet 192.168.26.0/24 --gateway 192.168.26.1 --ipam-opt com.docker.network.bridge.name=cpn -o ovs.bridge.nat_acl=protectcpn -d ovs cpn || exit 1
        # TODO: due to SBI dependencies, would require different configs for some of the same components
        # (e.g) SMF for NSA vs. SA. Run hybrid until can dynamically generate core configs depending on NSA/SA.
        DOCKERFILES="$DOCKERFILES -f core/epc.yml -f core/core.yml"
fi

if [[ "$UPN" -eq 1 ]] ; then
        docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=27 -o ovs.bridge.dpid=0x630 -o ovs.bridge.mode=nat --subnet 192.168.27.0/24 --gateway 192.168.27.1 --ipam-opt com.docker.network.bridge.name=upn -d ovs upn || exit 1
        DOCKERFILES="$DOCKERFILES -f core/upn.yml"
fi

if [[ "$RFN" -eq 1 ]] ; then
        docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=28 -o ovs.bridge.dpid=0x640 -o ovs.bridge.mode=flat --subnet 192.168.28.0/24 --ipam-opt com.docker.network.bridge.name=rfn -o ovs.bridge.nat_acl=protectrfn -d ovs rfn || exit
fi

if [[ "$RAN" -eq 1 ]] ; then
        docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=29 -o ovs.bridge.dpid=0x650 -o ovs.bridge.mode=routed --subnet 192.168.29.0/24 --gateway 192.168.29.1 --ipam-opt com.docker.network.bridge.name=ran -o ovs.bridge.nat_acl=protectran -d ovs ran || exit 1
fi

if [[ "$VUE" -eq 1 ]] ; then
        DOCKERFILES="$DOCKERFILES -f SIMULATED/srsran-enb.yml -f SIMULATED/srsran-ue.yml"
fi

if [[ "$GNB" -eq 1 ]] ; then
        DOCKERFILES="$DOCKERFILES -f SIMULATED/ueransim-gnb.yml -f SIMULATED/ueransim-ue.yml"
fi

if [[ "$BLADERF" -eq 1 ]] ; then
        export BLADERF_EARFCN
        DOCKERFILES="$DOCKERFILES -f SDR/bladerf.yml"
fi

if [[ "$ETTUS" -eq 1 ]] ; then
        export ETTUS_EARFCN
        uhd_find_devices
        DOCKERFILES="$DOCKERFILES -f SDR/ettus.yml"
fi

if [[ "$LIMESDR" -eq 1 ]] ; then
        export LIMESDR_EARFCN
        DOCKERFILES="$DOCKERFILES -f SDR/limesdr.yml"
fi

docker-compose $DOCKERFILES up -d --build || exit 1
echo "$DOCKERFILES" > /tmp/d5g-dockerfiles.txt

docker-compose $DOCKERFILES logs -f
