import time

import geopy.distance
import requests

from skybed.message_types import UAVData, UAVResponseModel, MetaData

uav_data: UAVData


def update_position_from_trajectory(virtual_seconds_since_last_update: float):
    new_altitude = uav_data.altitude + uav_data.vertical_speed * virtual_seconds_since_last_update

    distance_xy_obj = geopy.distance.geodesic(
        kilometers=uav_data.speed / 60 / 60 * virtual_seconds_since_last_update)

    # bearing is the direction in degrees
    uav_data.position = distance_xy_obj.destination(point=uav_data.position, bearing=uav_data.direction)

    # distance function erases altitude, so no +=
    uav_data.position.altitude = new_altitude


def post_new_position(ip: str):
    dump = UAVResponseModel(data=[uav_data],
                            meta=MetaData(origin="self_report", timestamp=time.time())).model_dump_json()
    print("dump", dump)
    # TODO move this to kafka
    r = requests.post(url=f'http://{ip}:8000/update', data=dump)
    print("Http response:", r.text)


def update_trajectory_from_collision_avoidance_msg(new_uav_data: UAVData):
    # we are the authority on position data, so we don't trust the position data in the requests
    uav_data.speed = new_uav_data.speed
    uav_data.direction = new_uav_data.direction
    uav_data.vertical_speed = new_uav_data.vertical_speed
