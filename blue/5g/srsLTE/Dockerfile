FROM ubuntu:20.04
MAINTAINER Charlie Lewis <clewis@iqt.org>
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install --no-install-recommends -yq \
     build-essential \
     ca-certificates \
     cmake \
     git \
     g++ \
     iperf \
     iperf3 \
     iproute2 \
     iputils-ping \
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
     net-tools \
     python3 \
     python3-pip \
     python3-mako \
     soapysdr-module-lms7 \
     soapysdr-tools \
     tcpdump \
     wget
RUN pip3 install -U requests
WORKDIR /root
COPY add_default_route.sh /root/add_default_route.sh
COPY start_srsue.sh /root/start_srsue.sh

RUN git clone https://github.com/Nuand/bladeRF.git -b 2021.03
RUN git clone https://github.com/EttusResearch/uhd.git -b v4.0.0.0
#RUN git clone https://github.com/srsRAN/srsRAN.git -b release_21_04

RUN git clone https://github.com/srsRAN/srsRAN.git -b release_20_04_2
RUN git clone https://github.com/pothosware/SoapySDR.git -b soapy-sdr-0.7.2
RUN git clone https://github.com/myriadrf/LimeSuite.git -b v20.10.0

# pinned FPGA/firmware (see "latest" on fpga/firmware pages)
RUN wget https://www.nuand.com/fpga/v0.12.0/hostedxA9.rbf
RUN wget https://www.nuand.com/fx3/bladeRF_fw_v2.4.0.img

WORKDIR /root/uhd/host
RUN mkdir build
WORKDIR /root/uhd/host/build
RUN cmake ../ && make -j `nproc` && make install && ldconfig

# https://github.com/Nuand/bladeRF
RUN mkdir -p /root/bladeRF/host/build
WORKDIR /root/bladeRF/host/build
RUN cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local .. && make -j && make install && ldconfig
# Should detect bladeRF:
# bladeRF-cli -p
# bladeRF-cli -e info -e version
# if firmware upgrade indicated:
# bladeRF-cli -f <firmware_file>
# if need to auto flash fpga
# bladeRF-cli -L hostedxA9.rbf

RUN /usr/local/lib/uhd/utils/uhd_images_downloader.py
# Should detect B200:
# uhd_find_devices

RUN mkdir -p /root/SoapySDR/build
WORKDIR /root/SoapySDR/build
RUN cmake ../ && make -j `nproc` && make install && ldconfig

RUN mkdir -p /root/LimeSuite/builddir
WORKDIR /root/LimeSuite/builddir
RUN cmake ../ && make -j `nproc` && make install && ldconfig

RUN mkdir -p /root/srsRAN/build
RUN mkdir /config
WORKDIR /root/srsRAN/build
RUN cmake ../ && make -j `nproc` && make install && ldconfig

ENTRYPOINT ["/bin/sh"]
