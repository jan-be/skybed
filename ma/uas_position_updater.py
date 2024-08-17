import time

import geopy
import requests
from geopy import Point
from geopy.distance import geodesic, distance

from ma.message_types import UAVData, UAVResponseModel, MetaData
from ma.ns3_interface import Ns3PerformanceParameters, get_ns3_sim_result

uavs_data = [
    UAVData(uav_id="001", uav_type="1", latitude=52.20237543416176, longitude=13.150412924715013, altitude=10000,
            speed=50, direction=70, vertical_speed=0),
    UAVData(uav_id="002", uav_type="1", latitude=52.20319075876912, longitude=13.155755910701549, altitude=10000,
            speed=50, direction=250, vertical_speed=0),
    UAVData(uav_id="003", uav_type="1", latitude=52.20390073751389, longitude=13.159446838052352, altitude=10000,
            speed=50, direction=250, vertical_speed=0),
    UAVData(uav_id="004", uav_type="1", latitude=52.204492415697864, longitude=13.164274813461564, altitude=10000,
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


def get_network_params_best_gnb(uav_data: UAVData) -> Ns3PerformanceParameters:
    closest_dist = float("inf")
    for gnb_position in gnb_positions:
        dist = distance(gnb_position, uav_data.position)
        closest_dist = min(closest_dist, dist)

    return get_ns3_sim_result(distance=closest_dist)


def post_new_position():
    dump = UAVResponseModel(data=uavs_data,
                            meta=MetaData(origin="self_report", timestamp=time.time())).model_dump_json()
    print("dump", dump)
    r = requests.post(url='http://localhost:8000/update', data=dump)
    print("hmm", r.text)


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


def loop_update_post_position():
    while True:
        post_new_position()
        time.sleep(1)
        update_position(1)
