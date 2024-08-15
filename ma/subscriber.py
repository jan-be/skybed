# code adapted from ChaosRez/6gn-functions/kafka/subscriber.py

from datetime import datetime

from confluent_kafka import Consumer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from pydantic import RootModel

from ma.message_types import UAVData
from ma.uas_position_updater import update_trajectory


def create_topic(topic_name):
    admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})   #NOTE: hardcoded credentials
    topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
    admin_client.create_topics([topic])

def create_consumer():
    conf = {'bootstrap.servers': "localhost:9092", 'group.id': "group1", 'auto.offset.reset': 'earliest'}
    consumer = Consumer(conf)
    return consumer

def listen_for_messages(consumer):
    consumer.subscribe(['releases'])

    try:
        while True:
            msg = consumer.poll(60.0)

            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                msg_str = msg.value().decode('utf-8')
                print(f'[{timestamp}] '+'Received message: {}'.format(msg_str))
                uavs_data = RootModel[list[UAVData]].model_validate_json(msg_str).root

                for uav_data in uavs_data:
                    update_trajectory(uav_data)



    except KeyboardInterrupt:
        pass

    finally:
        consumer.close()

def subscribe():
    create_topic('releases')
    consumer = create_consumer()
    listen_for_messages(consumer)