import segmentation_pb2 as msg
from kafka import KafkaConsumer, KafkaProducer
import os

"""
This file contains just test code that must be changed when catalog service will do there job and create necessary topics for us.
It sends some message to kafka and then reads it and append results to log/
"""

TOPIC = "eventTopic"
BOOTSTRAP_SERVER = [os.environ.get("S_CATALOG_KAFKA_HOST")]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
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
        print(data)
        producer_instance.send(topic, data.SerializeToString())
        producer_instance.flush()
        log.append("Message successfully sent")
    except Exception as e:
        log.append(str(e))


def get_message(consumer):
    links = []
    for message in consumer:
        value = message.value
        link = msg.Segmentation()
        link.ParseFromString(value)
        log.append("Message successfully received")
        log.append(str(link))
        links.append(link)
        return links


producer = connect_kafka_producer()
print("Poducer innitialized")
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
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
