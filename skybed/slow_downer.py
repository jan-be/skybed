import shlex
import subprocess

from skybed.message_types import UAVContainer
from skybed.ns3_interface import NetworkParams

tc_bin = "/sbin/tc"


def init_traffic_control(network_id: str):
    interface = f"br-{network_id[:12]}"

    add_root_qdisc_command = f"{tc_bin} qdisc add dev {interface} root handle 1: htb default 1 r2q 1"

    try:
        subprocess.run(shlex.split(add_root_qdisc_command), check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to init traffic control. Error: {e.stdout} {e.stderr}")


def slow_down_container_network(container: UAVContainer, network_params: NetworkParams):
    interface = f"br-{container.throttled_network_id[:12]}"

    if network_params.throughput == 0:
        network_params.packet_loss = 1
    else:
        # this is because the packet loss from 5g-LENA is really high,
        # and if we just copy it, we get approximately 0 MBit/s TCP throughput
        network_params.packet_loss = 0

    try:
        if not container.tc_class_added:
            add_class_command = f"{tc_bin} class add dev {interface} parent 1: classid 1:{container.id[:4]} htb rate 1000mbit quantum 1514"
            subprocess.run(shlex.split(add_class_command), check=True, capture_output=True, text=True)

        netem_command = f"{tc_bin} qdisc {'change' if container.tc_class_added else 'add'} dev {interface} parent 1:{container.id[:4]} handle {container.id[4:8]}: netem delay {network_params.delay}ms rate {network_params.throughput}mbit loss {network_params.packet_loss * 100}%"
        subprocess.run(shlex.split(netem_command), check=True, capture_output=True, text=True)

        if not container.tc_class_added:
            add_class_command = f"{tc_bin} filter add dev {interface} protocol ip parent 1:0 prio 3 u32 match ip dst {container.throttled_ip} flowid 1:{container.id[:4]}"
            subprocess.run(shlex.split(add_class_command), check=True, capture_output=True, text=True)

        container.tc_class_added = True
    except subprocess.CalledProcessError as e:
        print(f"Failed to slow down container with IP {container.throttled_ip}:\n{e.stdout} {e.stderr}")
