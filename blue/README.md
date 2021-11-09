# Blue Team
The following directory has a series of tools that are used for defending and building out environments for running scenarios in.

# 4G/5G Environment Creation Tool

## Dependencies
- Linux with a recent kernel
- Docker
- python3 and pip3
- uhd-host (`sudo apt-get install -y uhd-host`)

## Installation
The main tool in this directory is called `daedalus` and can be installed with easily with pip:

```
pip3 install daedalus-5g
```

or locally:

```
git clone https://github.com/IQTLabs/Daedalus
cd Daedalus/blue
sudo python3 setup.py install
```

Once installed, you can simply execute `daedalus` and you will be prompted for the 4G/5G environments you'd like it to create.

** Note **
```
AMD64 CPUs must support SSE4.1, AVX, AVX2, and FMA. If you don't have those, you can alternatively try starting daedalus with -b which will build the images locally and might work.

ARM64 CPUs don't have those requirements, but you will need g++ when pip installing for grpc.
```
