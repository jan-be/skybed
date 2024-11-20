import shlex
import subprocess
import sys
import threading
import time

import typer

from skybed.message_types import UAV
from skybed.ns3_interface import NetworkParams
from skybed.uav import position
from skybed.uav.internal_server import run_uav_server_async
from skybed.uav.position import update_position_from_trajectory
from skybed.uav.publisher import create_producer, publish_position_update
from skybed.uav.subscriber import subscribe

sys.stdout.reconfigure(line_buffering=True)

network_params: NetworkParams

typer = typer.Typer()

def run_iperf():
    try:
        subprocess.run(shlex.split("iperf3 -s"), check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"iperf3 failed: {e.stdout} {e.stderr}")


@typer.command()
def start_uav(ip: str, uav_id: str, uav_type: str, latitude: float, longitude: float, altitude: float, speed: float,
              direction: float, vertical_speed: float):
    position.uav = UAV(uav_id=uav_id, uav_type=uav_type, latitude=latitude, longitude=longitude,
                       altitude=altitude,
                       speed=speed, direction=direction, vertical_speed=vertical_speed)

    run_uav_server_async()

    create_producer(ip)

    threading.Thread(target=subscribe, args=[ip, position.uav.uav_id]).start()
    threading.Thread(target=run_iperf).start()

    update_hz = 50

    while True:
        publish_position_update(position.uav)
        time.sleep(1 / update_hz)
        update_position_from_trajectory(1 / update_hz)


if __name__ == "__main__":
    typer()
