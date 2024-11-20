import threading

import uvicorn
from fastapi import FastAPI

from skybed.uav import position

fast_api = FastAPI()


@fast_api.get("/uav")
async def get_uav():
    return position.uav


def run_uav_server_async():
    threading.Thread(target=uvicorn.run, args=["skybed.uav.internal_server:fast_api"],
                     kwargs={"host": "0.0.0.0", "port": 5000, "access_log": False}).start()
