import json
import logging
import os
import traceback

import requests
from kafka import KafkaConsumer
import logstash

import protobuf.favorites_updated_event_pb2 as favorites

TOPIC_FAVOURITE = "user-service-favorites-updated"
BOOTSTRAP_SERVER = [os.environ.get("S_USER_KAFKA_HOST")]  # ["localhost:29092"]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
GROUP_ID = "wine.user-service"  # consumer needs to be a part of a consumer group
OUR_ADDRESS = os.environ["S_OUR_ADDRESS"]
logstash_host = os.environ.get("S_LOGSTASH_HOST")

consumer_favourites = KafkaConsumer(
    TOPIC_FAVOURITE,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    group_id=GROUP_ID,
)

logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s:%(message)s', level=logging.INFO)
logger = logging.getLogger('kafka_reader')
logger.addHandler(logging.StreamHandler())
logger.addHandler(logstash.TCPLogstashHandler(host=logstash_host.split(":")[0],
                                              port=int(logstash_host.split(":")[1]),
                                              version=1,
                                              tags=["ml-team-2-service"]))

class OperationType:
    CREATE = 0
    DELETE = 1
    CLEAR = 3


def get_message_favourites(consumer):
    logger.info("Favourites updates")
    for message in consumer:
        message = message.value
        result = favorites.FavoritesUpdatedEvent()
        result.ParseFromString(message)

        try:
            if result.meta.operation_type == OperationType.CREATE:
                request_body = [{"rating": 1, "variants": 1, "wine": result.wineId, "user": result.userId}]
                response = requests.post(f"{OUR_ADDRESS}/review/", json=json.dumps(request_body))
                if response.status_code != 200:
                    logger.error(f"Adding new review with user id {result.userId} and wine id {result.wineId} failed")
                    logger.error(f"Code: {response.status_code}, response: {response.text}")
                else:
                    logger.info(f"Successfully adding new review with user id {result.userId} and wine id {result.wineId}")
            elif result.meta.operation_type == OperationType.DELETE:
                request_body = {"wine_id": result.wineId, "user_id": result.userId}
                response = requests.delete(f"{OUR_ADDRESS}/review/", json=json.dumps(request_body))
                if response.status_code != 200:
                    logger.error(f"Deleting review with user id {result.userId} and wine id {result.wineId} failed")
                    logger.error(f"Code: {response.status_code}, response: {response.text}")
                else:
                    logger.info(
                        f"Successfully deleting review with user id {result.userId} and wine id {result.wineId}")
            elif result.meta.operation_type == OperationType.CLEAR:
                request_body = {"user_id": result.userId}
                response = requests.delete(f"{OUR_ADDRESS}/review/", json=json.dumps(request_body))
                if response.status_code != 200:
                    logger.error(f"Deleting all reviews with user id {result.userId} failed")
                    logger.error(f"Code: {response.status_code}, response: {response.text}")
                else:
                    logger.info(
                        f"Successfully deleting all reviews with user id {result.userId}")
            else:
                logger.info("Skip not create operation type")
        except Exception:
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    get_message_favourites(consumer_favourites)
