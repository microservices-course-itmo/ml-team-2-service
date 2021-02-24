import os
import json
import requests
from tqdm import tqdm
import logging

OUR_ADDRESS = os.environ['S_OUR_ADDRESS']
CATALOG_ADDRESS = os.environ['S_CATALOG_ADDRESS']


def get_catalog_wines():
    logging.info("Started getting catalog wines")
    catalog_wines = requests.get(f"{CATALOG_ADDRESS}/wine/")
    if catalog_wines.status_code != 200:
        raise Exception("catalog_wines.status_code is not 200")
    logging.info("Finished getting catalog wines")
    return catalog_wines.json()


def get_our_wines():
    logging.info("Started getting our wines")
    our_wines = requests.get(f"{OUR_ADDRESS}/wines/")
    if our_wines.status_code != 200:
        raise Exception("our_wines.status_code is not 200")
    logging.info("Finished getting our wines")
    return our_wines.json()


def add_new_wine(wine: dict):
    body = {"internal_id": wine["wine_id"], "all_names": wine["name"]}
    response = requests.post(f"{OUR_ADDRESS}/wines/", json=body)
    if response.status_code != 200:
        logging.error(f"Adding wine with id {wine['wine_id']} failed")
        logging.error(response.status_code)
        logging.error(response.json())


def main():
    catalog_wines = get_catalog_wines()
    our_wines = get_our_wines()

    catalog_ids = set([wine["wine_id"] for wine in catalog_wines])
    our_ids = set([wine["internal_id"] for wine in our_wines if wine["internal_id"] != None])
    new_ids = catalog_ids - our_ids

    logging.info(f"Started adding new wines. Will be added {len(new_ids)} wines")
    request_body = []
    for wine in tqdm(catalog_wines):
        if wine["wine_id"] not in new_ids:
            continue
        request_body.append({"internal_id": wine["wine_id"], "all_names": wine["name"]})
    response = requests.post(f"{OUR_ADDRESS}/wines/", json=json.dumps(request_body))
    if response.status_code != 200:
        logging.error(f"Adding wines failed")
        logging.error(response.status_code)
        logging.error(response.text)
        raise Exception("Adding wines failed")
    logging.info(f"Finished adding new wines")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
