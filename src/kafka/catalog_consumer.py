import json
import logging
import os
import traceback

import requests
from kafka import KafkaConsumer

import protobuf.new_wine_saved_message_sent_event_pb2 as new_wine

TOPIC = "eventTopic"
BOOTSTRAP_SERVER = [os.environ.get("S_CATALOG_KAFKA_HOST")]
AUTO_OFFSET_RESET = "earliest"  # after breaking down consumer restarts reading at the latest commit offset
GROUP_ID = "wine.catalog-service"  # consumer needs to be a part of a consumer group
OUR_ADDRESS = os.environ["S_OUR_ADDRESS"]

consumer_new_wine = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVER,
    auto_offset_reset=AUTO_OFFSET_RESET,
    group_id=GROUP_ID,
)


def get_message_new_wine(consumer):
    logging.info("New wines")
    for message in consumer:
        message = message.value
        result = new_wine.NewWineSavedMessageSentEvent()
        result.ParseFromString(message)

        try:
            request_body = [{"internal_id": result.wineId, "all_names": result.wineName}]
            response = requests.post(f"{OUR_ADDRESS}/wines/", json=json.dumps(request_body))
            if response.status_code != 200:
                logging.error(f"Adding wine with id {result.wineId} and wine name {result.wineName} failed")
                logging.error(f"Code: {response.status_code}, response: {response.text}")
            else:
                logging.info(f"Successfully adding new wine wine with id {result.wineId} and wine name {result.wineName}")
        except Exception:
            logging.error(traceback.format_exc())

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s:%(message)s', level=logging.INFO)
    get_message_new_wine(consumer_new_wine)
