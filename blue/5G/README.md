# NOTE: docker-compose 1.29.1 or later is required.

# install the daedalus tool from source
```
pip3 install .
```

# install the daedalus tool from PyPi
```
pip3 install daedalus
```

# once services are running, if using virtual UEs, test virtual UE connectivity
```
docker exec -it ue ping 8.8.8.8
```
