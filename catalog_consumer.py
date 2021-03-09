import segmentation_pb2 as msg
from kafka import KafkaConsumer, KafkaProducer
from json import loads
import os

TOPIC = "eventTopic"
BOOTSTRAP_SERVER = ["localhost:9092"]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
ENABLE_AUTO_COMMIT = (
    True  # makes sure the consumer commits its read offset every interval
)
AUTO_COMMIT_INTERVAL = 1  # 1 second
GROUP_ID = "wine.catalog-service"  # consumer needs to be a part of a consumer group


def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=["localhost:9092"])
    except Exception:
        pass
    finally:
        return _producer


def publish_message(producer_instance, topic_name, data):
    try:
        producer_instance.send(
            topic_name, data.SerializeToString()
        )  # key=key_bytes, value=value_bytes)
        producer_instance.flush()
        print("Message successfully sent...\n")
    except Exception as e:
        print(str(e))


def get_message(consumer):
    messages = []
    for message in consumer:
        UpdatePriceEvent = message.value
        messages.append(UpdatePriceEvent)
        print(UpdatePriceEvent)
    return messages


producer = connect_kafka_producer()
print("Poducer innitialized")
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    # enable_auto_commit=ENABLE_AUTO_COMMIT,
    group_id=GROUP_ID,
)

segm = msg.Segmentation()
segm2 = msg.Segmentation()

segm.segm_link = "http://we`re_ml-2"
segm.mask_link = "http://ml-2_team"
segm.id = 1

print(segm)
# this is just to check locally if it`s working or not
publish_message(producer, TOPIC, segm)  #'msg', str(serialized))
links = get_message(consumer)
print(links)
