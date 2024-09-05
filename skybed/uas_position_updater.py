import threading
import time
import traceback

import requests
from geopy import Point

from skybed.helpers import geopy_3d_distance
from skybed.message_types import UAV
from skybed.ns3_interface import NetworkParams, get_ns3_sim_result
from skybed.scenarios.base_scenario import Scenario
from skybed.slow_downer import slow_down_container_network

uavs: list[UAV] = []
gnb_positions: list[Point] = []  # 5G connection not simulated when empty

currently_ns3_is_calculating_by_uav: list[str] = []


def poll_current_uav_status(uav: UAV):
    try:
        r = requests.get(url=f'http://{uav.container.unthrottled_ip}:5000/uav')
    except Exception:
        traceback.print_exc()

    new_uav = UAV.model_validate_json(r.text)

    # the container is not transmitted over the network, so restore it from last version
    new_uav.container = uav.container

    uavs[uavs.index(uav)] = new_uav


def get_network_params_best_gnb(uav: UAV) -> NetworkParams:
    closest_dist = float("inf")
    for gnb_position in gnb_positions:
        dist = geopy_3d_distance(gnb_position, uav.position)
        closest_dist = min(closest_dist, dist)

    return get_ns3_sim_result(distance=closest_dist)


def update_container_network(uav: UAV):
    currently_ns3_is_calculating_by_uav.append(uav.uav_id)

    performance_params = get_network_params_best_gnb(uav)
    print("performance_params UAV", uav.uav_id, performance_params)
    slow_down_container_network(uav.container, performance_params)

    currently_ns3_is_calculating_by_uav.remove(uav.uav_id)


def init_scenario(scenario: Scenario):
    uavs.extend(scenario.uavs)
    gnb_positions.extend(scenario.gnb_positions)


def loop_update_position_and_network_params():
    while True:
        time.sleep(1)

        for uav in uavs:
            poll_current_uav_status(uav)
            if uav.uav_id not in currently_ns3_is_calculating_by_uav:
                threading.Thread(target=update_container_network, args=[uav]).start()
