# code adapted from ChaosRez/6gn-functions/kafka/subscriber.py
import traceback
from datetime import datetime

from confluent_kafka import Consumer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from pydantic import RootModel

from skybed.message_types import UAV
from skybed.uav.position import update_trajectory_from_collision_avoidance_msg


def create_topic(topic_name, ip: str):
    admin_client = AdminClient({'bootstrap.servers': f'{ip}:9092'})
    topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
    fs = admin_client.create_topics([topic])

    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print(f"Topic {topic} created")
        except Exception as e:
            print(f"Failed to create topic {topic}: {e}")


def create_consumer(ip: str):
    conf = {'bootstrap.servers': f"{ip}:9092", 'group.id': f"group_{ip}", 'auto.offset.reset': 'earliest'}
    consumer = Consumer(conf)
    return consumer


def listen_for_messages(consumer, uav_id: str):
    consumer.subscribe(['releases'])

    try:
        while True:
            msg = consumer.poll(60.0)

            if msg is None:
                continue
            if msg.error():
                raise KafkaException(f"{uav_id}: {msg.error()}")
            else:
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                msg_str = msg.value().decode('utf-8')

                print("hmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm", msg.topic(), msg_str)
                uavs = RootModel[list[UAV]].model_validate_json(msg_str).root

                # ignore all parts of messages that are not related to the UAV associated with this thread
                for uav in uavs:
                    if uav.uav_id == uav_id:
                        print(f'[{timestamp}, {uav_id}] ' + 'Received message: {}'.format(msg_str))
                        update_trajectory_from_collision_avoidance_msg(uav)

    except Exception:
        traceback.print_exc()
    finally:
        print("consumer closed")
        consumer.close()


def subscribe(ip: str, uav_id: str):
    create_topic('releases', ip)
    create_topic('update', ip)
    consumer = create_consumer(ip)
    listen_for_messages(consumer, uav_id)
