import time

import geopy
import requests
from geopy import Point
from geopy.distance import geodesic
from importlib_metadata import metadata
from pandas.core.computation.expressions import where

from ma.message_types import UAVData, UAVResponseModel, MetaData

uavs_data = [
    UAVData(uav_id="001", uav_type="1",
            latitude=52.0, longitude=0.1, altitude=10000, speed=50, direction=90, vertical_speed=0),
    UAVData(uav_id="002", uav_type="1",
            latitude=52.0, longitude=0.2, altitude=10000, speed=50, direction=270, vertical_speed=0),
    UAVData(uav_id="003", uav_type="1",
            latitude=55.0, longitude=0.15, altitude=10000, speed=50, direction=270, vertical_speed=0),
    UAVData(uav_id="004", uav_type="1",
            latitude=55.0, longitude=0.25, altitude=10000, speed=50, direction=90, vertical_speed=0)
]


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
        time.sleep(5)
        update_position(1)
