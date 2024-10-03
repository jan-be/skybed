#!/usr/bin/env bash

for (( i = 1; i <= 30; i++ )); do
    v=$(($i * 20))
    echo "#####################################################"
    echo "UAV count: ${v}"
    sed -i "19s/.*/            for u in range(${v})]/" "skybed/scenarios/schoenhagen_many_drones.py"
    timeout -s SIGINT 15m poetry run skybed schoenhagen_many_drones
done
