import numpy as np


class Uas:
    pos = np.zeros(3)
    next_waypoint = np.zeros(3)


if __name__ == '__main__':
    uases = []
    while True:
        for uas in uases:
            uas.pos = np.zeros(3)  # receive from pilot
            if uas.pos > uas.next_waypoint:
                uas.next_waypoint = uas.pos + np.array([1, 1, 1])
                # send to pilot
