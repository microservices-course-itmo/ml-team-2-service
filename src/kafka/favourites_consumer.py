import json
import logging
import os
import traceback

import requests
from kafka import KafkaConsumer

import protobuf.favorites_updated_event_pb2 as favorites

TOPIC_FAVOURITE = "user-service-favorites-updated"
BOOTSTRAP_SERVER = [os.environ.get("S_USER_KAFKA_HOST")]  # ["localhost:29092"]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
GROUP_ID = "wine.user-service"  # consumer needs to be a part of a consumer group
OUR_ADDRESS = os.environ["S_OUR_ADDRESS"]

consumer_favourites = KafkaConsumer(
    TOPIC_FAVOURITE,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    group_id=GROUP_ID,
)


class OperationType:
    CREATE = 0
    DELETE = 1
    CLEAR = 3


def get_message_favourites(consumer):
    logging.info("Favourites updates")
    for message in consumer:
        message = message.value
        result = favorites.FavoritesUpdatedEvent()
        result.ParseFromString(message)

        try:
            if result.meta.operation_type == OperationType.CREATE:
                request_body = [{"rating": 1, "variants": 1, "wine": result.wineId, "user": result.userId}]
                response = requests.post(f"{OUR_ADDRESS}/review/", json=json.dumps(request_body))
                if response.status_code != 200:
                    logging.error(f"Adding new review with user id {result.userId} and wine id {result.wineId} failed")
                    logging.error(f"Code: {response.status_code}, response: {response.text}")
                else:
                    logging.info(f"Successfully adding new review with user id {result.userId} and wine id {result.wineId}")
            elif result.meta.operation_type == OperationType.DELETE:
                request_body = {"wine_id": result.wineId, "user_id": result.userId}
                response = requests.delete(f"{OUR_ADDRESS}/review/", json=json.dumps(request_body))
                if response.status_code != 200:
                    logging.error(f"Deleting review with user id {result.userId} and wine id {result.wineId} failed")
                    logging.error(f"Code: {response.status_code}, response: {response.text}")
                else:
                    logging.info(
                        f"Successfully deleting review with user id {result.userId} and wine id {result.wineId}")
            elif result.meta.operation_type == OperationType.CLEAR:
                request_body = {"user_id": result.userId}
                response = requests.delete(f"{OUR_ADDRESS}/review/", json=json.dumps(request_body))
                if response.status_code != 200:
                    logging.error(f"Deleting all reviews with user id {result.userId} failed")
                    logging.error(f"Code: {response.status_code}, response: {response.text}")
                else:
                    logging.info(
                        f"Successfully deleting all reviews with user id {result.userId}")
            else:
                logging.info("Skip not create operation type")
        except Exception:
            logging.error(traceback.format_exc())


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s:%(message)s', level=logging.INFO)
    get_message_favourites(consumer_favourites)
