import os
import json
import requests
from tqdm import tqdm
import logging

OUR_ADDRESS = os.environ["S_OUR_ADDRESS"]
USER_ADDRESS = os.environ["S_USER_ADDRESS"]


def get_app_users_id():
    logging.warning("Started getting app users")
    app_users_id = []
    current_page = 0
    total_pages = 1
    while current_page < total_pages:
        logging.warning(f"Current page - {current_page} of {total_pages}")
        url = f"{USER_ADDRESS}/internal/users?page={current_page}&size=20"
        app_users = requests.get(url)
        if app_users.status_code != 200:
            raise Exception(f"app_users.status_code is not 200, {app_users.status_code}, {app_users}, {app_users.text}, {url}")

        app_users_dict = app_users.json()
        app_users_id.extend([user["id"] for user in app_users_dict["content"]])

        total_pages = app_users_dict["totalPages"]
        current_page += 1

    logging.warning("Finished getting app users")
    return app_users_id


def get_our_users_id():
    logging.warning("Started getting our users")
    our_users = requests.get(f"{OUR_ADDRESS}/users/")
    if our_users.status_code != 200:
        raise Exception("our_wines.status_code is not 200")
    our_users_dict = our_users.json()
    our_users_id = [user["internal_id"] for user in our_users_dict]
    logging.warning("Finished getting our wines")
    return our_users_id


def user_sync_job():
    app_users_id = get_app_users_id()
    our_users_id = get_our_users_id()

    new_ids = set(app_users_id) - set(our_users_id)

    logging.warning(f"Started adding new users. Will be added {len(new_ids)} users")
    request_body = []
    for id_ in tqdm(new_ids):
        request_body.append({"internal_id": id_})
    response = requests.post(f"{OUR_ADDRESS}/users/", json=json.dumps(request_body))
    if response.status_code != 200:
        logging.error(f"Adding users failed")
        logging.error(response.status_code)
        logging.error(response.text)
        raise Exception("Adding users failed")
    logging.warning(f"Finished adding new users")


if __name__ == "__main__":
    user_sync_job()
