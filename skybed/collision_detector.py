import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from skybed.scenarios.base_scenario import Scenario


# based on https://stackoverflow.com/questions/10549402/kdtree-for-longitude-latitude
def detect_collisions(scenario: Scenario):
    for uav in scenario.uavs:
        uav.currently_in_collision = False

    uavs_df = pd.DataFrame(data={
        'name': [u.uav_id for u in scenario.uavs],
        'lat': [u.latitude for u in scenario.uavs],
        'lon': [u.longitude for u in scenario.uavs]
    })

    bt = BallTree(np.deg2rad(uavs_df[['lat', 'lon']].values))
    radius = scenario.collision_radius / 6_378_137  # 100 meters
    collisions, distances = bt.query_radius(np.deg2rad(uavs_df[['lat', 'lon']].values), r=radius, count_only=False,
                                            return_distance=True)

    for collision in collisions:
        if len(collision) > 1:
            scenario.uavs[collision[0]].currently_in_collision = True
            scenario.uavs[collision[1]].currently_in_collision = True
            scenario.uavs[collision[0]].previously_in_collision = True
            scenario.uavs[collision[1]].previously_in_collision = True
            print(f"collision occured between {scenario.uavs[collision[0]].uav_id} and {scenario.uavs[collision[1]].uav_id}")
