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
     iputils-ping \
     unzip \
     libzmq3-dev \
     build-essential \
     git \
     ca-certificates \
     iproute2 \
     tcpdump \
     net-tools \
     iperf \
     iperf3 \
     libpcsclite-dev \
     lksctp-tools
WORKDIR /root
COPY add_default_route.sh /root/add_default_route.sh
COPY start_srsue.sh /root/start_srsue.sh

RUN git clone https://github.com/srsLTE/srsLTE.git

RUN mkdir -p /root/srsLTE/build
RUN mkdir /config

WORKDIR /root/srsLTE/build
RUN cmake ../
RUN make -j `nproc`
RUN make install
RUN ldconfig

ENTRYPOINT ["/bin/sh"]
