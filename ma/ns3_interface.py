# adapted from jan-be/5G-neural-network/simulator/dataset_generation.py

import re
import shlex
import subprocess as sp

from pydantic import BaseModel


class Ns3PerformanceParameters(BaseModel):
    delay: float
    jitter: float
    throughput: float
    packet_loss: float


def get_ns3_sim_result(distance: float) -> Ns3PerformanceParameters:
    # 49 dbm from https://www.techplayon.com/5g-nr-total-transmit-power-maximum-cell-transmit-power-reference-signal-power/

    process = sp.Popen(
        shlex.split(f'docker run --rm carnegie ./ns3 run "cttc-nr-mimo-demo --txPowerGnb=49 --gnbUeDistance={distance}"'),
        stdout=sp.PIPE,
        stderr=sp.PIPE, shell=False)

    raw_ns3_out = ""
    for line in process.stdout.readlines():
        raw_ns3_out += line.decode("utf-8")

    sim_result_vars_names = ["Tx Packets", "Rx Packets", "Mean delay", "Mean jitter", "Throughput"]
    sim_results = {}

    for var in sim_result_vars_names:
        sim_results[var] = float(re.findall(var + r':[ \t]+([-+]?(?:\d*\.*\d+))', raw_ns3_out)[0])

    return Ns3PerformanceParameters(
        delay=sim_results["Mean delay"],
        jitter=sim_results["Mean jitter"],
        throughput=sim_results["Throughput"],
        packet_loss=1 - sim_results["Rx Packets"] / sim_results["Tx Packets"]
    )


if __name__ == '__main__':
    print(get_ns3_sim_result(distance=500))
