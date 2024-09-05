from skybed.message_types import UAV
from skybed.scenarios.base_scenario import Scenario


class SimpleCollisionUK(Scenario):
    uavs = [
        UAV(uav_id="001", uav_type="1",
            latitude=52.0, longitude=0.1, altitude=10000, speed=50, direction=90, vertical_speed=0),
        UAV(uav_id="002", uav_type="1",
            latitude=52.0, longitude=0.2, altitude=10000, speed=50, direction=270, vertical_speed=0),
        UAV(uav_id="003", uav_type="1",
            latitude=55.0, longitude=0.15, altitude=10000, speed=50, direction=270, vertical_speed=0),
        UAV(uav_id="004", uav_type="1",
            latitude=55.0, longitude=0.25, altitude=10000, speed=50, direction=90, vertical_speed=0)
    ]

    gnb_positions = []
