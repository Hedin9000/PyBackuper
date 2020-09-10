import os
import shutil
from os import listdir
from os.path import isfile, join
import json
import logging

ConfigFilePath = 'config.json'


def create_dir_if_not_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)


def move_to_dir(file_path, destination_path):
    create_dir_if_not_exist(os.path.dirname(destination_path))
    if os.path.exists(destination_path):
        os.remove(destination_path)
    shutil.copytree(file_path, destination_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    with open(ConfigFilePath) as json_file:
        data = json.load(json_file)
        for store_item in data['StoreItems']:
            if store_item['Enabled']:
                destination_dir = os.path.join(data['RootFolder'], store_item['InnerPath'])
                move_to_dir(store_item['Path'], destination_dir)
                logging.info(f"{store_item['Name']} successfully stored to {store_item['InnerPath']}")


if __name__ == "__main__":
    main()
