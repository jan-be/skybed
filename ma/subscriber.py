# code adapted from ChaosRez/6gn-functions/kafka/subscriber.py
import threading
from datetime import datetime

from confluent_kafka import Consumer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from pydantic import RootModel

from ma.message_types import UAVData
from ma.uas_position_updater import update_trajectory


def create_topic(topic_name, ip: str):
    admin_client = AdminClient({'bootstrap.servers': f'{ip}:9092'})  # NOTE: hardcoded credentials
    topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
    admin_client.create_topics([topic])


def create_consumer(ip: str):
    conf = {'bootstrap.servers': f"{ip}:9092", 'group.id': f"group_{ip}", 'auto.offset.reset': 'earliest'}
    consumer = Consumer(conf)
    return consumer


def listen_for_messages(consumer, ip: str, uav_id: str):
    consumer.subscribe(['releases'])

    try:
        while True:
            msg = consumer.poll(60.0)

            if msg is None:
                continue
            if msg.error():
                print(ip)
                raise KafkaException(msg.error())
            else:
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                msg_str = msg.value().decode('utf-8')
                uavs_data = RootModel[list[UAVData]].model_validate_json(msg_str).root

                # ignore all parts of messages that are not related to the UAV associated with this thread
                for uav_data in uavs_data:
                    if uav_data.uav_id == uav_id:
                        print(f'[{timestamp}, {ip}] ' + 'Received message: {}'.format(msg_str))
                        update_trajectory(uav_data)



    except KeyboardInterrupt:
        pass

    finally:
        consumer.close()


def subscribe(ip: str, uav_id: str):
    create_topic('releases', ip)
    consumer = create_consumer(ip)
    listen_for_messages(consumer, ip, uav_id)


if __name__ == '__main__':
    ips = [f"172.{x}.0.2" for x in range(25, 29)]
    print(ips)
    for ip in ips:
        threading.Thread(target=subscribe, args=[ip]).start()
