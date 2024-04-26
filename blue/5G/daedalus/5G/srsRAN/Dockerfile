FROM ubuntu:24.04 as cloner
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ARG SRS_VERSION=release_23_11
ENV DEBIAN_FRONTEND noninteractive
# hadolint ignore=DL3008
RUN apt-get update && apt-get install --no-install-recommends -yq ca-certificates git
WORKDIR /src
RUN git clone https://github.com/EttusResearch/uhd.git -b v4.4.0.0 && \
  git clone https://github.com/Nuand/bladeRF.git -b 2023.02 && \
  git clone https://github.com/pothosware/SoapySDR.git -b soapy-sdr-0.8.1 && \
  git clone https://github.com/srsRAN/srsRAN.git -b ${SRS_VERSION}

FROM ubuntu:24.04 as depbuilder
ENV DEBIAN_FRONTEND noninteractive
# hadolint ignore=DL3008
RUN apt-get update && apt-get install --no-install-recommends -yq \
     build-essential \
     ca-certificates \
     cmake \
     g++ \
     git \
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
     pkg-config \
     python3 \
     python3-pip \
     python3-mako \
     soapysdr-module-lms7 \
     soapysdr-tools
# hadolint ignore=DL3013
RUN python3 -m pip install -U pip requests
COPY --from=cloner /src /src
WORKDIR /src/uhd/host/build
RUN cmake -DENABLE_TESTS=OFF -DENABLE_MANUAL=OFF -DENABLE_EXAMPLES=OFF -DENABLE_B100=OFF -DENABLE_USRP1=OFF -DENABLE_USRP2=OFF -DENABLE_X300=OFF -DENABLE_N320=OFF -DENABLE_N300=OFF -DENABLE_E320=OFF -DENABLE_E300=OFF -DENABLE_X400=OFF -DENABLE_MPMD=OFF -DENABLE_OCTOCLOCK=OFF -DCMAKE_FIND_LIBRARY_SUFFIXES=".a" -DBUILD_SHARED_LIBS=OFF ../ && make -j "$(nproc)" && make install && ldconfig
WORKDIR /src/bladeRF/host/build
RUN cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local -DCMAKE_FIND_LIBRARY_SUFFIXES=".a" -DBUILD_SHARED_LIBS=OFF .. && make -j "$(nproc)" && make install && ldconfig
WORKDIR /src/SoapySDR/build
RUN cmake -DCMAKE_FIND_LIBRARY_SUFFIXES=".a" -DBUILD_SHARED_LIBS=OFF ../ && make -j "$(nproc)" && make install && ldconfig

FROM ubuntu:24.04 as srsbuilder
ENV DEBIAN_FRONTEND noninteractive
# hadolint ignore=DL3008
RUN apt-get update && apt-get install --no-install-recommends -yq \
     build-essential \
     ca-certificates \
     cmake \
     g++ \
     git \
     libboost-chrono-dev \
     libboost-date-time-dev \
     libboost-filesystem-dev \
     libboost-program-options-dev \
     libboost-thread-dev \
     libboost-test-dev \
     libconfig++-dev \
     libfftw3-dev \
     libmbedtls-dev \
     libsctp-dev \
     libzmq3-dev

COPY --from=cloner /src/srsRAN /src/srsRAN
COPY --from=depbuilder /usr/local /usr/local/
WORKDIR /src/srsRAN/build
RUN cmake -DENABLE_AVX512=OFF -DCMAKE_FIND_LIBRARY_SUFFIXES=".a" -DBUILD_SHARED_LIBS=OFF ../ && make -j "$(nproc)" && make install && ldconfig

FROM ubuntu:24.04
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV DEBIAN_FRONTEND noninteractive
COPY --from=srsbuilder /usr/local /usr/local
RUN apt-get update && apt-get install --no-install-recommends -yq \
     iperf \
     iperf3 \
     iproute2 \
     iputils-ping \
     libmbedcrypto7 \
     libfftw3-3 \
     libboost-chrono1.74.0 \
     libboost-filesystem1.74.0 \
     libboost-thread1.74.0 \
     libboost-program-options1.74.0 \
     libconfig++9v5 \
     libtecla1 \
     libusb-1.0-0 \
     libzmq5 \
     lksctp-tools \
     python3 \
     net-tools \
     tcpdump \
     wget && \
     apt-get autoremove && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN /usr/local/bin/srsue --help && /usr/local/bin/srsenb --help && /usr/local/bin/bladeRF-cli --help
RUN /usr/local/lib/uhd/utils/uhd_images_downloader.py -t "b2|usb"
RUN mkdir /config
COPY scripts /scripts
ENTRYPOINT ["/bin/sh"]
