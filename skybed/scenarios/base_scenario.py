from geopy import Point

from skybed.message_types import UAV


class Scenario:
    uavs: list[UAV]
    gnb_positions: list[Point]  # 5G connection not simulated when empty
