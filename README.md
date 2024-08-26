# Skybed
*A Software Testbed for Anti-Collision Systems for Drones leveraging 6G Edge Computing*

## Install

- Install Docker, Python 3.11 or newer, Poetry
- Setup [6gn-functions](https://github.com/ChaosRez/6gn-functions) 
- Setup [tinyFaas](https://github.com/OpenFogStack/tinyFaaS) and modify it to support build tools
- Then clone this repo and its directory run:
```shell
poetry install

# to allow changing the network configuration without superuser privileges
# from https://tcconfig.readthedocs.io/en/latest/pages/usage/execute_not_super_user.html
# the following execution binary paths may be different for each environment:
sudo setcap cap_net_admin+ep /sbin/tc
sudo setcap cap_net_raw,cap_net_admin+ep /bin/ip

# this will take a while
docker build -f ns3_lena.Dockerfile -t ns3_lena .
docker build -f uav.Dockerfile -t uav .
```

## Run
in the tinyFaas directory
```shell
make start
```

in the 6gn-functions directory
```shell
./start_all.sh
```

in this repo's directory
```shell
skybed
```