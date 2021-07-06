FROM ubuntu:21.04
MAINTAINER Charlie Lewis <clewis@iqt.org>
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install --no-install-recommends -yq \
     build-essential \
     ca-certificates \
     cmake \
     git \
     g++ \
     iproute2 \
     libsctp-dev \
     lksctp-tools \
     tcpdump \
     iputils-ping \
     make
RUN git clone https://github.com/aligungr/UERANSIM
WORKDIR /UERANSIM
RUN make
COPY scripts /scripts
ENTRYPOINT ["/bin/sh"]
