import os
import json
import requests
from tqdm import tqdm
import logging
import logstash

OUR_ADDRESS = os.environ["S_OUR_ADDRESS"]
USER_ADDRESS = os.environ["S_USER_ADDRESS"]
logstash_host = os.environ.get("S_LOGSTASH_HOST")


def get_app_favorites():
    logger.info("Started getting app users")
    favorites = []
    app_users = requests.get(f"{USER_ADDRESS}/internal/users/favorites")
    if app_users.status_code != 200:
        raise Exception("app_users.status_code is not 200")

    app_users_favorites = app_users.json()

    for user_favorites in app_users_favorites:
        user_id = user_favorites["userId"]
        for wine_id in user_favorites["favoriteIds"]:
            favorites.append((wine_id, user_id))

    logger.info("Finished getting app users")
    return favorites


def main():
    app_favorites = get_app_favorites()
    logger.info(f"Started adding new favorites")
    request_body = []
    for wine_id, user_id in tqdm(app_favorites):
        request_body.append(
            {"rating": 5, "variants": 5, "wine": wine_id, "user": user_id}
        )
    response = requests.post(f"{OUR_ADDRESS}/review/", json=json.dumps(request_body))
    if response.status_code != 200:
        logger.error(f"Adding favorites failed")
        logger.error(response.status_code)
        logger.error(response.text)
        raise Exception("Adding favorites failed")
    logger.info(f"Finished sync favorites")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('kafka_reader')
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(logstash.TCPLogstashHandler(host=logstash_host.split(":")[0],
                                                  port=int(logstash_host.split(":")[1]),
                                                  version=1))
    main()