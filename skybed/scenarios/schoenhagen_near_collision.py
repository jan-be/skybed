from geopy import Point

from skybed.message_types import UAV
from skybed.scenarios.base_scenario import Scenario


class SchoenhagenNearCollision(Scenario):
    uavs = [
        UAV(uav_id="001", uav_type="1", latitude=52.20237543416176, longitude=13.150412924715013, altitude=300,
            speed=50, direction=70, vertical_speed=0),
        UAV(uav_id="002", uav_type="1", latitude=52.20319075876912, longitude=13.155755910701549, altitude=300,
            speed=50, direction=250, vertical_speed=0),
        UAV(uav_id="003", uav_type="1", latitude=52.20390073751389, longitude=13.159446838052352, altitude=300,
            speed=50, direction=250, vertical_speed=0),
        UAV(uav_id="004", uav_type="1", latitude=52.204492415697864, longitude=13.164274813461564, altitude=300,
            speed=50, direction=70, vertical_speed=0)
    ]

    gnb_positions = [
        Point(52.202822869219, 13.160761351939868, 40),
        Point(52.207789905972355, 13.160182908727288, 40),
        Point(52.20998760863871, 13.150075547198409, 40)
    ]

    use_precomputed_network_params = True
