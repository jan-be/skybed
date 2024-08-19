import shlex
import subprocess

from ma.ns3_interface import Ns3PerformanceParameters


def slow_down_container_network(network_id: str, perf_params: Ns3PerformanceParameters):
    interface = f"br-{network_id[:12]}"

    tcset_str = f"--overwrite --rate {perf_params.throughput}mbps --delay {perf_params.delay}ms"
    try:
        # TODO make incoming work without superuser privileges
        # subprocess.run(shlex.split(f"tcset {interface} --direction incoming {tcset_str}"), check=True)
        subprocess.run(shlex.split(f"tcset {interface} --direction outgoing {tcset_str}"), check=True)

    except subprocess.CalledProcessError as e:
        print(f"Failed to slow down the container. Error: {e}")
