import json
import logging
import os
import traceback

import requests
from kafka import KafkaConsumer

import protobuf.user_updated_event_pb2 as user

TOPIC_USERS = "user-service-user-updated"  # needed to be changed
BOOTSTRAP_SERVER = [os.environ.get("S_USER_KAFKA_HOST")]  # ["localhost:29092"]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
GROUP_ID = "wine.user-service"  # consumer needs to be a part of a consumer group
OUR_ADDRESS = os.environ["S_OUR_ADDRESS"]

consumer_users = KafkaConsumer(
    TOPIC_USERS,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    group_id=GROUP_ID,
)


def get_message_user(consumer):
    logging.info("User updates")
    for message in consumer:
        message = message.value
        result = user.UserUpdatedEvent()
        result.ParseFromString(message)

        try:
            if result.meta.operation_type == 0:  # if type is create
                request_body = [{"internal_id": result.userId}]
                response = requests.post(f"{OUR_ADDRESS}/users/", json=json.dumps(request_body))
                if response.status_code != 200:
                    logging.error(f"Adding user with id {result.userId} failed")
                    logging.error(f"Code: {response.status_code}, response: {response.text}")
                else:
                    logging.info(f"Successfully adding new user with id {result.userId}")
            else:
                logging.info("Skip not create operation type")
        except Exception:
            logging.error(traceback.format_exc())


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s:%(message)s', level=logging.INFO)
    get_message_user(consumer_users)
