import asyncio
import math

from geopy import Point
from geopy.distance import distance


def geopy_3d_distance(a: Point, b: Point) -> float:
    distance_2d = distance((a.latitude, a.longitude), (b.latitude, b.longitude)).meters

    altitude_difference = b.altitude - a.altitude

    return math.sqrt(distance_2d ** 2 + altitude_difference ** 2)

# from https://stackoverflow.com/questions/48483348/how-to-limit-concurrency-with-python-asyncio
async def gather_with_concurrency(n, *coros):
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro
    return await asyncio.gather(*(sem_coro(c) for c in coros))
