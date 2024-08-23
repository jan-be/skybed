import threading

import uvicorn
from fastapi import FastAPI

from skybed.uav import position

fast_api = FastAPI()


@fast_api.get("/uav_data")
def get_uav_data():
    return position.uav_data


def run_uav_server_async():
    threading.Thread(target=uvicorn.run, args=["skybed.uav.internal_server:fast_api"],
                     kwargs={"host": "0.0.0.0", "port": 5000, "log_level": "info"}).start()
