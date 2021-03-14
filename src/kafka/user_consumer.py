from kafka import KafkaConsumer
from json import loads
import os
import json
import favorites_updated_event_pb2 as favorites
import user_updated_event_pb2 as user

TOPIC_USERS = "user-service-user-updated"  # needed to be changed
TOPIC_FAVOURITE = "user-service-favorites-updated"
BOOTSTRAP_SERVER = ["localhost:29092"]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
ENABLE_AUTO_COMMIT = (
    True  # makes sure the consumer commits its read offset every interval
)
AUTO_COMMIT_INTERVAL = 1  # 1 second
GROUP_ID = "wine.user-service"  # consumer needs to be a part of a consumer group

consumer_users = KafkaConsumer(
    TOPIC_USERS,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    # enable_auto_commit=ENABLE_AUTO_COMMIT,
    group_id=GROUP_ID,
)

consumer_favourites = KafkaConsumer(
    TOPIC_FAVOURITE,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    # enable_auto_commit=ENABLE_AUTO_COMMIT,
    group_id=GROUP_ID,
)


def get_message_favourites(consumer):
    print("Favourites updates")
    messages = []
    for message in consumer:
        message = message.value
        messages.append(message)
        link = favorites.FavoritesUpdatedEvent()
        link.ParseFromString(message)
        print(link)
    return messages


def get_message_user(consumer):
    print("User updates")
    messages = []
    for message in consumer:
        message = message.value
        messages.append(message)
        link = user.UserUpdatedEvent()
        link.ParseFromString(message)
        print(link)
    return messages


if __name__ == "__main__":
    # get_message_favourites(consumer_favourites)
    get_message_user(consumer_users)
