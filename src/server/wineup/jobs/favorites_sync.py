import os
import json
import requests
from tqdm import tqdm
import logging

OUR_ADDRESS = os.environ["S_OUR_ADDRESS"]
USER_ADDRESS = os.environ["S_USER_ADDRESS"]


def get_app_favorites():
    logging.warning("Started getting app users")
    favorites = []
    app_users = requests.get(f"{USER_ADDRESS}/internal/users/favorites")
    if app_users.status_code != 200:
        raise Exception(f"app_users.status_code is not 200, {app_users.status_code}, {app_users}, {app_users.text}")

    app_users_favorites = app_users.json()

    for user_favorites in app_users_favorites:
        user_id = user_favorites["userId"]
        for wine_id in user_favorites["favoriteIds"]:
            favorites.append((wine_id, user_id))

    logging.warning("Finished getting app users")
    return favorites


def favorites_sync_job():
    app_favorites = get_app_favorites()
    logging.warning(f"Started adding new favorites")
    request_body = []
    for wine_id, user_id in tqdm(app_favorites):
        request_body.append(
            {"rating": 5, "variants": 5, "wine": wine_id, "user": user_id}
        )
    response = requests.post(f"{OUR_ADDRESS}/review/", json=json.dumps(request_body))
    if response.status_code != 200:
        logging.error(f"Adding favorites failed")
        logging.error(response.status_code)
        logging.error(response.text)
        raise Exception("Adding favorites failed")
    logging.warning(f"Finished sync favorites")


if __name__ == "__main__":
    favorites_sync_job()
