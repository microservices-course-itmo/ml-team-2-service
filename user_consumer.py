from kafka import KafkaConsumer
from json import loads
import os

<<<<<<< Updated upstream
TOPIC = "eventTopic"  # needed to be changed
# BOOTSTRAP_SERVER = [os.environ.get('S_KAFKA_BOOTSTRAP_HOST')]
BOOTSTRAP_SERVER = ["localhost:9092"]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
ENABLE_AUTO_COMMIT = (
    True  # makes sure the consumer commits its read offset every interval
)
AUTO_COMMIT_INTERVAL = 1  # 1 second
GROUP_ID = "wine.user-service"  # consumer needs to be a part of a consumer group
=======
TOPIC_USERS = 'service-user-updated' # needed to be changed
TOPIC_FAVOURITE = 'user-service-favorites-updated'
BOOTSTRAP_SERVER = ['kafka:9092']
AUTO_OFFSET_RESET = 'earliest' # after breaking down consumer restarts reading at the latest commit offset
ENABLE_AUTO_COMMIT = True # makes sure the consumer commits its read offset every interval
AUTO_COMMIT_INTERVAL = 1 # 1 second
GROUP_ID = 'wine.user-service' # consumer needs to be a part of a consumer group
>>>>>>> Stashed changes

consumer_users = KafkaConsumer(
    TOPIC_USERS,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    #enable_auto_commit=ENABLE_AUTO_COMMIT,
    group_id=GROUP_ID,
)

consumer_favourites = KafkaConsumer(
    TOPIC_FAVOURITE,
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
<<<<<<< Updated upstream
=======
    return messages
>>>>>>> Stashed changes
