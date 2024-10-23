#!/usr/bin/env bash

for (( i = 1; i <= 30; i++ )); do
    v=$(($i * 20))
    echo "#####################################################"
    echo "UAV count: ${v}"
    sed -i "19s/.*/            for u in range(${v})]/" "../skybed/scenarios/schoenhagen_many_drones.py"
    poetry run skybed schoenhagen_many_drones
    docker stop $(docker ps -a -q)
    docker network prune -f
done
