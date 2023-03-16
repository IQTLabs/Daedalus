#!/bin/sh

export DEBIAN_FRONTEND=noninteractive && \
  echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections
  sudo apt-get update && \
  sudo apt-get remove docker docker-engine docker.io containerd runc && \
  sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common nftables && \
  sudo update-alternatives --set iptables /usr/sbin/iptables-legacy && \
  sudo nft flush ruleset && \
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
  sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io python3-setuptools python3-dev uhd-host && \
  sudo python3 -m pip install -U pip && \
  sudo python3 -m pip install "./blue[generate_fs,confuser,test]"
