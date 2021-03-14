import segmentation_pb2 as msg
from kafka import KafkaConsumer, KafkaProducer
from json import loads

"""
This file contains code that must be changed when catalog service will do there job and create necessary topics for us
"""

TOPIC = "eventTopic"
BOOTSTRAP_SERVER = ["localhost:29092"]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
ENABLE_AUTO_COMMIT = (
    True  # makes sure the consumer commits its read offset every interval
)
AUTO_COMMIT_INTERVAL = 1  # 1 second
GROUP_ID = "wine.catalog-service"  # consumer needs to be a part of a consumer group

log = []


def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=["kafka:29092"])
    except Exception:
        log.append("producer connection failed")
        pass
    finally:
        log.append("producer connection success")
        return _producer


def publish_message(producer_instance, topic_name, data):
    try:
        # key_bytes = bytes(str(key), encoding='utf-8')
        # value_bytes = bytes(str(value), encoding='utf-8')
        # print(data)
        print(data)
        producer_instance.send(
            topic, data.SerializeToString()
        )  # key=key_bytes, value=value_bytes)
        producer_instance.flush()
        log.append("Message successfully sent")
    except Exception as e:
        log.append(str(e))


def get_message(consumer):
    links = []
    for message in consumer:
        value = message.value
        link = msg.Segmentation()
        # link.ParseFromString(value)
        log.append("Message successfully received")
        # log.append(str(link))
        links.append(link)
        return links


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

segm.segm_link = "http://nowhere"
segm.mask_link = "http://non-existent"
segm.id = 1

# serialized = segm.SerializeToString()

log.append(str(segm))

publish_message(producer, TOPIC, segm)  #'msg', str(serialized))
links = get_message(consumer)

log.append(str(links[0]))

d = {}
for i in range(len(log)):
    d.update({"line " + str(i): log[i]})
print(links)
