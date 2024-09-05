import geopy.distance

from skybed.message_types import UAV
from skybed.uav.publisher import publish_position_update

uav: UAV


def update_position_from_trajectory(virtual_seconds_since_last_update: float):
    new_altitude = uav.altitude + uav.vertical_speed * virtual_seconds_since_last_update

    distance_xy_obj = geopy.distance.geodesic(
        kilometers=uav.speed / 60 / 60 * virtual_seconds_since_last_update)

    # bearing is the direction in degrees
    uav.position = distance_xy_obj.destination(point=uav.position, bearing=uav.direction)

    # distance function erases altitude, so no +=
    uav.position.altitude = new_altitude


def post_new_position():
    publish_position_update(uav)


def update_trajectory_from_collision_avoidance_msg(new_uav: UAV):
    # we are the authority on position data, so we don't trust the position data in the requests
    uav.speed = new_uav.speed
    uav.direction = new_uav.direction
    uav.vertical_speed = new_uav.vertical_speed
