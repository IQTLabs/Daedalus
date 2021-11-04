FROM ubuntu:20.04 AS builder
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
     libpcsclite-dev \
     libtecla-dev \
     libusb-1.0-0-dev \
     libvolk2-dev \
     python3 \
     python3-pip \
     python3-mako \
     soapysdr-module-lms7 \
     soapysdr-tools && \
     apt-get autoremove && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip3 install -U requests
WORKDIR /root

RUN git clone https://github.com/EttusResearch/uhd.git -b v4.1.0.1 \
    && mkdir -p /root/uhd/host/build \
    && cd /root/uhd/host/build \
    && cmake -DENABLE_TESTS=OFF -DENABLE_MANUAL=OFF -DENABLE_EXAMPLES=OFF -DENABLE_B100=OFF -DENABLE_USRP1=OFF -DENABLE_USRP2=OFF -DENABLE_X300=OFF -DENABLE_N320=OFF -DENABLE_N300=OFF -DENABLE_E320=OFF -DENABLE_E300=OFF -DENABLE_X400=OFF -DENABLE_MPMD=OFF -DENABLE_OCTOCLOCK=OFF ../ && make -j `nproc` && make install && ldconfig \
    && cd /root && rm -rf /root/uhd

RUN git clone https://github.com/Nuand/bladeRF.git -b 2021.03 \
    && mkdir -p /root/bladeRF/host/build \
    && cd /root/bladeRF/host/build \
    && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local .. && make -j && make install && ldconfig \
    && cd /root && rm -rf /root bladeRF

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

FROM ubuntu:20.04 AS srsran
ARG SRS_VERSION=release_21_04
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
     libmbedtls-dev \
     libfftw3-dev \
     libsctp-dev \
     libzmq3-dev \
     lksctp-tools \
     pkg-config && \
     apt-get autoremove && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/srsRAN/srsRAN.git -b ${SRS_VERSION} \
    && mkdir -p /srsRAN/build \
    && cd /srsRAN/build \
    && cmake -DENABLE_AVX512=OFF ../ && make -j `nproc` && make install && ldconfig

FROM ubuntu:20.04
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
COPY --from=builder /usr/local /usr/local
COPY --from=srsran /usr/local /usr/local
COPY --from=builder /usr/lib/*-linux-gnu /usr/lib/
COPY --from=srsran /usr/lib/*-linux-gnu /usr/lib/
ENV DEBIAN_FRONTEND noninteractive
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
WORKDIR /root
COPY scripts /scripts
ENTRYPOINT ["/bin/sh"]
