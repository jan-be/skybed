import math

from geopy import Point
from geopy.distance import distance


def geopy_3d_distance(a: Point, b: Point) -> float:
    distance_2d = distance((a.latitude, a.longitude), (b.latitude, b.longitude)).meters

    altitude_difference = b.altitude - a.altitude

    return math.sqrt(distance_2d ** 2 + altitude_difference ** 2)
