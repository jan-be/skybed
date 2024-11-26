import asyncio
import multiprocessing

import aiohttp
from aiohttp import ClientConnectionError

from skybed.collision_detector import detect_collisions
from skybed.helpers import geopy_3d_distance, gather_with_concurrency
from skybed.message_types import UAV
from skybed.ns3_interface import NetworkParams, get_ns3_sim_result
from skybed.precompute_network_params import get_closest_ns3_sim_result
from skybed.scenarios.base_scenario import Scenario
from skybed.slow_downer import slow_down_container_network

scenario: Scenario = Scenario()

currently_ns3_is_calculating_by_uav: list[str] = []


async def poll_current_uav_status(uav: UAV, session: aiohttp.ClientSession):
    try:
        async with session.get(f'http://{uav.container.unthrottled_ip}:5000/uav', timeout=0.1) as resp:
            json_str = await resp.text()

            new_uav = UAV.model_validate_json(json_str)

            # the container and evaluation are not transmitted over the network, so restore them from last version
            # maybe refactor this at some point
            new_uav.container = uav.container
            new_uav.evaluation = uav.evaluation
            new_uav.previously_in_collision = uav.previously_in_collision
            new_uav.currently_in_collision = uav.currently_in_collision
            new_uav.evaluation = uav.evaluation

            scenario.uavs[scenario.uavs.index(uav)] = new_uav

            uav.evaluation.poll_response_count += 1
    except (TimeoutError, ConnectionRefusedError, ClientConnectionError):
        uav.evaluation.poll_no_response_count += 1


async def get_network_params_best_gnb(uav: UAV) -> NetworkParams:
    closest_dist = float("inf")
    for gnb_position in scenario.gnb_positions:
        dist = geopy_3d_distance(gnb_position, uav.position)
        closest_dist = min(closest_dist, dist)

    if scenario.use_precomputed_network_params:
        return get_closest_ns3_sim_result(distance=closest_dist)
    else:
        return await get_ns3_sim_result(distance=closest_dist)


async def update_container_network(uav: UAV):
    currently_ns3_is_calculating_by_uav.append(uav.uav_id)

    performance_params = await get_network_params_best_gnb(uav)
    print("performance_params UAV", uav.uav_id, performance_params)
    slow_down_container_network(uav.container, performance_params)

    currently_ns3_is_calculating_by_uav.remove(uav.uav_id)

    uav.evaluation.network_update_count += 1


def init_scenario(sce: Scenario):
    scenario.uavs = sce.uavs
    scenario.gnb_positions = sce.gnb_positions
    if len(sce.gnb_positions) == 0:
        scenario.throttle_cellular = False
    else:
        scenario.throttle_cellular = sce.throttle_cellular
    scenario.use_precomputed_network_params = sce.use_precomputed_network_params
    scenario.collision_radius = sce.collision_radius


async def loop_update_position():
    async with aiohttp.ClientSession() as session:

        while True:
            await asyncio.sleep(0.1)

            # get UAV positions via HTTP GET
            polling_sessions = []
            for uav in scenario.uavs:
                polling_sessions.append(asyncio.create_task(poll_current_uav_status(uav, session)))
            await asyncio.gather(*polling_sessions)

            detect_collisions(scenario)


async def loop_update_network_params():
    if scenario.throttle_cellular:
        while True:
            await asyncio.sleep(0.5)

            coroutines = [update_container_network(uav) for uav in scenario.uavs if
                          uav.uav_id not in currently_ns3_is_calculating_by_uav]

            await gather_with_concurrency(multiprocessing.cpu_count(), *coroutines)
