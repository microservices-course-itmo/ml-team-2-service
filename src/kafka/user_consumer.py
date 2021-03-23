from kafka import KafkaConsumer
import os
import protobuf.favorites_updated_event_pb2 as favorites
import protobuf.user_updated_event_pb2 as user

TOPIC_USERS = "user-service-user-updated"  # needed to be changed
TOPIC_FAVOURITE = "user-service-favorites-updated"
BOOTSTRAP_SERVER = [os.environ.get("S_USER_KAFKA_HOST")]  # ["localhost:29092"]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
GROUP_ID = "wine.user-service"  # consumer needs to be a part of a consumer group

consumer_users = KafkaConsumer(
    TOPIC_USERS,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    group_id=GROUP_ID,
)

consumer_favourites = KafkaConsumer(
    TOPIC_FAVOURITE,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    group_id=GROUP_ID,
)


def get_message_favourites(consumer):
    print("Favourites updates")
    messages = []
    for message in consumer:
        message = message.value
        messages.append(message)
        result = favorites.FavoritesUpdatedEvent()
        result.ParseFromString(message)
        print(result)
    return messages


def get_message_user(consumer):
    print("User updates")
    messages = []
    for message in consumer:
        message = message.value
        messages.append(message)
        result = user.UserUpdatedEvent()
        result.ParseFromString(message)
        print(result)
    return messages


if __name__ == "__main__":
    """
    Suppose this 2 functions should work in parallel, will make it later
    """
    # get_message_favourites(consumer_favourites)
    get_message_user(consumer_users)
