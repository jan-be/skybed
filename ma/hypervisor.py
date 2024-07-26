import docker

from ma import map_visualizer, world_positions, hypervisor_position_server

if __name__ == '__main__':
    client = docker.from_env()

    # image = client.images.build(path=".", tag="hmm")
    # print(image)

    containers_gnb = []
    containers_uas = []

    for i in range(len(world_positions.gnb_positions[:, 0])):
        containers_gnb.append(client.containers.run(image="guide", name=f"guide_{i}", detach=True, remove=True))

    ipam_pool = docker.types.IPAMPool(
        subnet='192.168.51.0/24',
        gateway='192.168.51.254'
    )
    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool]
    )
    network = client.networks.create(
        f"network_uases_2",
        driver="bridge",
        ipam=ipam_config)

    for i in range(len(world_positions.uas_positions[:, 0])):
        containers_uas.append(client.containers.run(image="pilot", name=f"pilot_{i}", detach=True, remove=True))
        network.connect(f"pilot_{i}", ipv4_address=f"192.168.51.{i+1}")
        world_positions.ip_uas_map[f"192.168.51.{i+1}"] = i

    map_visualizer.run_map_server_async()
    hypervisor_position_server.run_position_server_async()

    print(containers_gnb + containers_uas)

    network.remove()

    for con in containers_gnb + containers_uas:
        con.stop()
