import threading
import time

import geopy
import requests
from geopy import Point
from geopy.distance import geodesic, distance

from ma.helpers import geopy_3d_distance
from ma.message_types import UAVData, UAVResponseModel, MetaData
from ma.ns3_interface import Ns3PerformanceParameters, get_ns3_sim_result
from ma.slow_downer import slow_down_container_network

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


def get_network_params_best_gnb(uav_data: UAVData) -> Ns3PerformanceParameters:
    closest_dist = float("inf")
    for gnb_position in gnb_positions:
        dist = geopy_3d_distance(gnb_position, uav_data.position)
        closest_dist = min(closest_dist, dist)

    return get_ns3_sim_result(distance=closest_dist)


def post_new_positions(uav_net_map):
    for uav_data in uavs_data:
        post_new_position(uav_data, uav_net_map[uav_data.uav_id]["ip"])


def post_new_position(uav_data: UAVData, ip):
    dump = UAVResponseModel(data=[uav_data],
                            meta=MetaData(origin="self_report", timestamp=time.time())).model_dump_json()
    print("dump", dump)
    # TODO throttling localhost is difficult.
    #      Maybe it can be achieved by throtting on an HTTP level
    #      Or maybe Reza will do /update using message brokering like for mutate
    r = requests.post(url=f'http://localhost:8000/update', data=dump)
    print("Http response:", r.text)


def update_position(virtual_seconds_since_last_update: float):
    for uav_data in uavs_data:
        new_altitude = uav_data.altitude + uav_data.vertical_speed * virtual_seconds_since_last_update

        distance_xy_obj = geopy.distance.geodesic(
            kilometers=uav_data.speed / 60 / 60 * virtual_seconds_since_last_update)

        # bearing is the direction in degrees
        uav_data.position = distance_xy_obj.destination(point=uav_data.position, bearing=uav_data.direction)

        # distance function erases altitude, so no +=
        uav_data.position.altitude = new_altitude


# we cannot trust the position data in the requests, because there might be latency
def update_trajectory(new_uav_data: UAVData):
    uav_data = [uav_data for uav_data in uavs_data if uav_data.uav_id == new_uav_data.uav_id][0]
    uav_data.speed = new_uav_data.speed
    uav_data.direction = new_uav_data.direction
    uav_data.vertical_speed = new_uav_data.vertical_speed


def update_container_network(uav_data: UAVData, uav_net_map):
    currently_ns3_is_calculating_by_uav[uav_data.uav_id] = True

    performance_params = get_network_params_best_gnb(uav_data)
    print("performance_params UAV", uav_data.uav_id, performance_params)
    slow_down_container_network(uav_net_map[uav_data.uav_id]["network_id"], performance_params)

    currently_ns3_is_calculating_by_uav[uav_data.uav_id] = False


def loop_update_post_position(uav_net_map):
    while True:
        post_new_positions(uav_net_map)
        time.sleep(5)
        update_position(1)

        for uav_data in uavs_data:
            if not currently_ns3_is_calculating_by_uav[uav_data.uav_id]:
                threading.Thread(target=update_container_network, args=(uav_data, uav_net_map)).start()
