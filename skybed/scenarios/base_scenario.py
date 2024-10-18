from geopy import Point

from skybed.message_types import UAV


class Scenario:
    uavs: list[UAV] = []
    gnb_positions: list[Point] = []
    throttle_cellular: bool = True
    use_precomputed_network_params: bool = False
    collision_radius: float = 100  # in meters
