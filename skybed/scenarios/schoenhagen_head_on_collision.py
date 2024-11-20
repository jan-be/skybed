from geopy import Point

from skybed.message_types import UAV
from skybed.scenarios.base_scenario import Scenario


class SchoenhagenHeadOnCollision(Scenario):
    uavs = [
        UAV(uav_id="001", uav_type="1", latitude=52.208226, longitude=13.157225, altitude=300,
            speed=170, direction=126, vertical_speed=0),
        UAV(uav_id="002", uav_type="1", latitude=52.206906, longitude=13.160194, altitude=300,
            speed=170, direction=180 + 126, vertical_speed=0),
    ]

    gnb_positions = [
        Point(52.202822869219, 13.160761351939868, 40),
        Point(52.207789905972355, 13.160182908727288, 40),
        Point(52.20998760863871, 13.150075547198409, 40)
    ]

    use_precomputed_network_params = True
    collision_radius = 10  # in meters
