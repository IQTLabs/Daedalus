FROM dorowu/ubuntu-desktop-lxde-vnc
RUN apt-get update && apt-get install -y mongodb
RUN mkdir -p /data/db
COPY ssh_server_fork.patch /ssh_server_fork.patch
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ssh_host_dsa_key /etc/ssh/ssh_host_dsa_key
COPY ssh_host_dsa_key.pub /etc/ssh/ssh_host_dsa_key.pub
COPY ssh_host_rsa_key /etc/ssh/ssh_host_rsa_key
COPY ssh_host_rsa_key.pub /etc/ssh/ssh_host_rsa_key.pub
COPY ssh_host_ecdsa_key /etc/ssh/ssh_host_ecdsa_key
COPY ssh_host_ecdsa_key.pub /etc/ssh/ssh_host_ecdsa_key.pub
COPY imsi1.json /root/imsi1.json

RUN set -ex \
    && BUILDDEP="gcc g++ make pkg-config cmake xz-utils patch" \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        ca-certificates \
        wget \
        libc6-dev \
        zlib1g-dev \
        libgcrypt20-dev \
        libgpg-error-dev \
        $BUILDDEP \
    && wget -qO- https://www.libssh.org/files/0.8/libssh-0.8.1.tar.xz \
        | xz -c -d | tar x -C /usr/src --strip-components=1 \
    && mkdir -p /usr/src/build \
    && patch /usr/src/examples/ssh_server_fork.c < /ssh_server_fork.patch \
    && cd /usr/src/build \
    && cmake \
        -DCMAKE_INSTALL_PREFIX=/usr \
        -DWITH_SERVER=ON \
        -DWITH_STATIC_LIB=ON \
        -DWITH_GSSAPI=ON \
        -DWITH_GCRYPT=ON \
        -DWITH_SFTP=ON \
        -DWITH_THREADS=ON \
        .. \
    && make && make install \
    && apt-get purge -y --auto-remove $BUILDDEP
