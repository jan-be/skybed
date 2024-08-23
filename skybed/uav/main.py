import threading
import time

import typer

from skybed.message_types import UAVData
from skybed.ns3_interface import NetworkParams
from skybed.uav import position
from skybed.uav.internal_server import run_uav_server_async
from skybed.uav.position import post_new_position, update_position_from_trajectory
from skybed.uav.subscriber import subscribe

network_params: NetworkParams

typer = typer.Typer()


@typer.command()
def start_uav(ip: str, uav_id: str, uav_type: str, latitude: float, longitude: float, altitude: float, speed: float,
              direction: float, vertical_speed: float):
    position.uav_data = UAVData(uav_id=uav_id, uav_type=uav_type, latitude=latitude, longitude=longitude,
                                altitude=altitude,
                                speed=speed, direction=direction, vertical_speed=vertical_speed)

    run_uav_server_async()
    threading.Thread(target=subscribe, args=[ip, position.uav_data.uav_id]).start()

    while True:
        post_new_position(ip)
        time.sleep(1)
        update_position_from_trajectory(1)


if __name__ == "__main__":
    typer()