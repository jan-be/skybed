import time
import requests

import numpy as np

if __name__ == '__main__':
    uas_pos = np.zeros(3)
    uas_next_waypoint = np.zeros(3)
    while True:
        r = requests.get('http://host.docker.internal:5000/position')
        pos = r.json()
        print(f"pos from http: {pos}")

        uas_next_waypoint = np.zeros(3)  # always listen to guide
        uas_pos += np.ones(3) * 0.1
        time.sleep(0.1)
        print(uas_pos)
