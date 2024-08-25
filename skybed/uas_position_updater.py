import threading
import time

import requests
from geopy import Point

from skybed.helpers import geopy_3d_distance
from skybed.message_types import UAVData
from skybed.ns3_interface import NetworkParams, get_ns3_sim_result
from skybed.slow_downer import slow_down_container_network

uavs_data = [
    UAVData(uav_id="001", uav_type="1", latitude=52.20237543416176, longitude=13.150412924715013, altitude=300,
            speed=50, direction=70, vertical_speed=0),
    UAVData(uav_id="002", uav_type="1", latitude=52.20319075876912, longitude=13.155755910701549, altitude=300,
            speed=50, direction=250, vertical_speed=0),
    UAVData(uav_id="003", uav_type="1", latitude=52.20390073751389, longitude=13.159446838052352, altitude=300,
            speed=50, direction=250, vertical_speed=0),
    UAVData(uav_id="004", uav_type="1", latitude=52.204492415697864, longitude=13.164274813461564, altitude=300,
            speed=50, direction=70, vertical_speed=0)
]
# uavs_data = [
#     UAVData(uav_id="001", uav_type="1",
#             latitude=52.20237543416176, longitude=13.150412924715013, altitude=10000, speed=50, direction=70, vertical_speed=0),
#     UAVData(uav_id="002", uav_type="1",
#             latitude=52.20319075876912, longitude=13.155755910701549, altitude=10000, speed=50, direction=250, vertical_speed=0),
#     UAVData(uav_id="003", uav_type="1",
#             latitude=52.20390073751389, longitude=13.159446838052352, altitude=10000, speed=50, direction=250, vertical_speed=0),
#     UAVData(uav_id="004", uav_type="1",
#             latitude=52.204492415697864, longitude=13.164274813461564, altitude=10000, speed=50, direction=70, vertical_speed=0)
# ]
# uavs_data = [
#     UAVData(uav_id="001", uav_type="1",
#             latitude=52.0, longitude=0.1, altitude=10000, speed=50, direction=90, vertical_speed=0),
#     UAVData(uav_id="002", uav_type="1",
#             latitude=52.0, longitude=0.2, altitude=10000, speed=50, direction=270, vertical_speed=0),
#     UAVData(uav_id="003", uav_type="1",
#             latitude=55.0, longitude=0.15, altitude=10000, speed=50, direction=270, vertical_speed=0),
#     UAVData(uav_id="004", uav_type="1",
#             latitude=55.0, longitude=0.25, altitude=10000, speed=50, direction=90, vertical_speed=0)
# ]
gnb_positions = [
    Point(52.202822869219, 13.160761351939868, 40),
    Point(52.207789905972355, 13.160182908727288, 40),
    Point(52.20998760863871, 13.150075547198409, 40)
]

currently_ns3_is_calculating_by_uav = {u.uav_id: False for u in uavs_data}


def poll_current_uav_status(uav_data: UAVData):
    r = requests.get(url=f'http://{uav_data.container.unthrottled_ip}:5000/uav_data')
    new_uav_data = UAVData.model_validate_json(r.text)

    # the container is not transmitted over the network, so restore it from last version
    new_uav_data.container = uav_data.container

    uavs_data[uavs_data.index(uav_data)] = new_uav_data
    print("new UAV data:", new_uav_data)


def get_network_params_best_gnb(uav_data: UAVData) -> NetworkParams:
    closest_dist = float("inf")
    for gnb_position in gnb_positions:
        dist = geopy_3d_distance(gnb_position, uav_data.position)
        closest_dist = min(closest_dist, dist)

    return get_ns3_sim_result(distance=closest_dist)


def update_container_network(uav_data: UAVData):
    currently_ns3_is_calculating_by_uav[uav_data.uav_id] = True

    performance_params = get_network_params_best_gnb(uav_data)
    print("performance_params UAV", uav_data.uav_id, performance_params)
    slow_down_container_network(uav_data.container.throttled_network_id, performance_params)

    currently_ns3_is_calculating_by_uav[uav_data.uav_id] = False


def loop_update_position_and_network_params():
    while True:
        time.sleep(0.1)

        for uav_data in uavs_data:
            poll_current_uav_status(uav_data)
            if not currently_ns3_is_calculating_by_uav[uav_data.uav_id]:
                threading.Thread(target=update_container_network, args=[uav_data]).start()
