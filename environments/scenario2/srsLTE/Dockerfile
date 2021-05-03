FROM ubuntu:20.04
MAINTAINER Charlie Lewis <clewis@iqt.org>
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install --no-install-recommends -yq \
     cmake \
     libuhd-dev \
     uhd-host \
     libboost-program-options-dev \
     libvolk2-dev \
     libfftw3-dev \
     libmbedtls-dev \
     libsctp-dev \
     libconfig++-dev \
     curl \
     unzip \
     libzmq3-dev \
     build-essential \
     git \
     ca-certificates \
     iproute2 \
     libpcsclite-dev \
     lksctp-tools \
     wget \
     tcpdump \
     net-tools \
     iputils-ping \
     iperf \
     iperf3
WORKDIR /root
COPY add_default_route.sh /root/add_default_route.sh
COPY start_srsue.sh /root/start_srsue.sh

RUN git clone https://github.com/srsRAN/srsRAN.git -b release_21_04_pre

RUN mkdir -p /root/srsRAN/build
RUN mkdir /config
WORKDIR /root/srsRAN/build
RUN cmake ../ && make -j `nproc` && make install && ldconfig

ENTRYPOINT ["/bin/sh"]
