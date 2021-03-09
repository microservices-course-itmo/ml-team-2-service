from kafka import KafkaConsumer
from json import loads
import os

TOPIC = "eventTopic"  # needed to be changed
# BOOTSTRAP_SERVER = [os.environ.get('S_KAFKA_BOOTSTRAP_HOST')]
BOOTSTRAP_SERVER = ["localhost:9092"]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
ENABLE_AUTO_COMMIT = (
    True  # makes sure the consumer commits its read offset every interval
)
AUTO_COMMIT_INTERVAL = 1  # 1 second
GROUP_ID = "wine.user-service"  # consumer needs to be a part of a consumer group

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    # enable_auto_commit=ENABLE_AUTO_COMMIT,
    group_id=GROUP_ID,
)


def get_message(consumer):
    messages = []
    for message in consumer:
        message = message.value
        messages.append(message)
        print(message)
