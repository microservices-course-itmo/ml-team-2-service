from kafka import KafkaConsumer
import protobuf.new_wine_saved_message_sent_event_pb2 as new_wine
import os

"""
This file contains just test code that must be changed when catalog service will do there job and create necessary topics for us.
It sends some message to kafka and then reads it and append results to log/
"""

TOPIC = "eventTopic"
BOOTSTRAP_SERVER = [os.environ.get("S_CATALOG_KAFKA_HOST")]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
GROUP_ID = "wine.catalog-service"  # consumer needs to be a part of a consumer group

consumer_new_wine = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    group_id=GROUP_ID,
)


def get_message_new_wine(consumer):
    print("New wines")
    messages = []
    for message in consumer:
        value = message.value
        messages.append(message)
        result = new_wine.NewWineSavedMessageSentEvent()
        result.ParseFromString(value)
        print(result)
    return messages


if __name__ == "__main__":
    get_message_new_wine(consumer_new_wine)
