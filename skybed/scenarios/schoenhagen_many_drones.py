import random

from geopy import Point

from skybed.message_types import UAV
from skybed.scenarios.base_scenario import Scenario

random.seed(0)


class SchoenhagenManyDrones(Scenario):
    uavs = [UAV(uav_id=f"{u}", uav_type="1",
                latitude=52.20237543416176 + random.uniform(-1e-2, 1e-2),
                speed=random.uniform(40, 60),
                vertical_speed=random.uniform(-10, 10),
                direction=random.uniform(0, 360),
                longitude=13.150412924715013 + random.uniform(-1e-2, 1e-2),
                altitude=300 + random.uniform(-100, 100))
            for u in range(200)]

    gnb_positions = [
        Point(52.202822869219, 13.160761351939868, 40),
        Point(52.207789905972355, 13.160182908727288, 40),
        Point(52.20998760863871, 13.150075547198409, 40)
    ]

    # throttle_cellular = False
    use_precomputed_network_params = True