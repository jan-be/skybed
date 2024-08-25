import shlex
import subprocess

from skybed.ns3_interface import NetworkParams


def slow_down_container_network(network_id: str, network_params: NetworkParams):
    interface = f"br-{network_id[:12]}"

    if network_params.packet_loss == 1:
        tcset_str = f"--overwrite --loss 100%"
    else:
        tcset_str = f"--overwrite --rate {network_params.throughput}mbps --delay {network_params.delay}ms"

    print("slowing down now:", tcset_str)

    # tcconfig for some reason sometimes causes a pyroute2.netlink.exceptions.NetlinkDumpInterrupted exception.
    # I don't know why, but it usually disappears, if you try again.
    i = 0
    while i < 4:
        try:
            # TODO make incoming work without superuser privileges
            # subprocess.run(shlex.split(f"tcset {interface} --direction incoming {tcset_str}"), check=True)
            subprocess.run(shlex.split(f"tcset {interface} --direction outgoing {tcset_str}"), check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to slow down the container. Error: {e}")
        else:
            break
