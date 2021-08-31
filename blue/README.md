# Blue Team
The following directory has a series of tools that are used for defending and building out environments for running scenarios in.

# 4G/5G Environment Creation Tool
The main tool in this directory is called `daedalus` and can be installed with `pip3 install daedalus-5g` or locally:
```
git clone https://github.com/IQTLabs/Daedalus
cd Daedalus/blue
sudo python3 setup.py install
```

Once installed, you can simply execute `daedalus` and you will be prompted for the 4G/5G environments you'd like it to create.

** Note **
```
CPU must support SSE4.1, AVX, AVX2, and FMA
```
