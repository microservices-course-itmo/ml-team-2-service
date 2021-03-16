import os
import json
import requests
from tqdm import tqdm
import logging

OUR_ADDRESS = os.environ["S_OUR_ADDRESS"]
USER_ADDRESS = os.environ["S_USER_ADDRESS"]


def get_app_favorites():
    # TODO: получение любимых вин
    logging.info("Started getting app users")
    app_users_id = []
    current_page = 0
    total_pages = 1
    while current_page < total_pages:
        logging.info(f"Current page - {current_page} of {total_pages}")
        app_users = requests.get(
            f"{USER_ADDRESS}/internal/users?page={current_page}&size=1"
        )
        if app_users.status_code != 200:
            raise Exception("app_users.status_code is not 200")

        app_users_dict = app_users.json()
        app_users_id.extend([user["id"] for user in app_users_dict["content"]])

        total_pages = app_users_dict["totalPages"]
        current_page += 1

    logging.info("Finished getting app users")
    return app_users_id


def main():
    app_favorites = get_app_favorites()
    logging.info(f"Started adding new favorites")
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
    logging.info(f"Finished sync favorites")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
