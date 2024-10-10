#!/usr/bin/env bash

for (( i = 0; i < 5; i++ )); do
    poetry run skybed schoenhagen_many_drones
    #doing those breaks tinyfaas
    #docker stop $(docker ps -a -q)
    #docker network prune -f
done
