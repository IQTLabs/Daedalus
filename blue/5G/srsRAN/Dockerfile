FROM ubuntu:20.04 as builder
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ARG SRS_VERSION=release_22_04
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install --no-install-recommends -yq \
     build-essential \
     ca-certificates \
     cmake \
     git \
     g++ \
     libboost-chrono-dev \
     libboost-date-time-dev \
     libboost-filesystem-dev \
     libboost-program-options-dev \
     libboost-thread-dev \
     libboost-test-dev \
     libconfig++-dev \
     libedit-dev \
     libfftw3-dev \
     libmbedtls-dev \
     libpcsclite-dev \
     libsctp-dev \
     libtecla-dev \
     libusb-1.0-0-dev \
     libvolk2-dev \
     libzmq3-dev \
     lksctp-tools \
     pkg-config \
     python3 \
     python3-pip \
     python3-mako \
     soapysdr-module-lms7 \
     soapysdr-tools
WORKDIR /root
RUN python3 -m pip install -U pip
RUN python3 -m pip install -U requests
RUN git clone https://github.com/EttusResearch/uhd.git -b v4.1.0.3 \
    && mkdir -p /root/uhd/host/build \
    && cd /root/uhd/host/build \
    && cmake -DENABLE_TESTS=OFF -DENABLE_MANUAL=OFF -DENABLE_EXAMPLES=OFF -DENABLE_B100=OFF -DENABLE_USRP1=OFF -DENABLE_USRP2=OFF -DENABLE_X300=OFF -DENABLE_N320=OFF -DENABLE_N300=OFF -DENABLE_E320=OFF -DENABLE_E300=OFF -DENABLE_X400=OFF -DENABLE_MPMD=OFF -DENABLE_OCTOCLOCK=OFF ../ && make -j `nproc` && make install && ldconfig \
    && cd /root && rm -rf /root/uhd
RUN git clone https://github.com/Nuand/bladeRF.git -b 2021.10 \
    && mkdir -p /root/bladeRF/host/build \
    && cd /root/bladeRF/host/build \
    && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local .. && make -j && make install && ldconfig \
    && cd /root && rm -rf /root/bladeRF
RUN git clone https://github.com/pothosware/SoapySDR.git -b soapy-sdr-0.7.2 \
    && mkdir -p /root/SoapySDR/build \
    && cd /root/SoapySDR/build \
    && cmake ../ && make -j `nproc` && make install && ldconfig \
    && cd /root && rm -rf /root/SoapySDR
RUN git clone https://github.com/myriadrf/LimeSuite.git -b v20.10.0 \
    && mkdir -p /root/LimeSuite/build \
    && cd /root/LimeSuite/build \
    && cmake ../ && make -j `nproc` && make install && ldconfig \
    && cd /root && rm -rf /root/LimeSuite
RUN /usr/local/lib/uhd/utils/uhd_images_downloader.py -t "b2|usb"
# TODO: not possible to build release 19_12 under Ubuntu 22.04 w/gcc 12,
# as string safety checks fail. If disabled with -Wno-error, srsRAN does
# not pass tests anyway.
RUN git clone https://github.com/srsRAN/srsRAN.git -b ${SRS_VERSION} \
    && mkdir -p /root/srsRAN/build \
    && cd /root/srsRAN/build \
    && cmake -DENABLE_AVX512=OFF ../ && make -j `nproc` && make install && ldconfig

FROM ubuntu:20.04
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV DEBIAN_FRONTEND noninteractive
COPY --from=builder /usr/local /usr/local
COPY --from=builder /usr/lib/*-linux-gnu /usr/lib/
RUN apt-get update && apt-get install --no-install-recommends -yq \
     iperf \
     iperf3 \
     iproute2 \
     iputils-ping \
     net-tools \
     tcpdump \
     wget && \
     apt-get autoremove && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN mkdir /config
COPY scripts /scripts
ENTRYPOINT ["/bin/sh"]
