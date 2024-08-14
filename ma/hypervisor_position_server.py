import threading

import uvicorn
from fastapi import FastAPI, Request

from ma import schoenhagen_positions

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/position")
def get_position(request: Request):
    print(f"hmmm ip {request.client.host}")
    uas_id = schoenhagen_positions.ip_uas_map[request.client.host]

    print(f"{request.client.host}: {uas_id}: {schoenhagen_positions[uas_id]}")

    return {"position": schoenhagen_positions[uas_id]}


def run_position_server_async():
    threading.Thread(target=uvicorn.run, args=["hypervisor_position_server:app"],
                     kwargs={"host": "0.0.0.0", "port": 5000, "log_level": "info"}).start()
    print("done")


if __name__ == '__main__':
    run_position_server_async()
