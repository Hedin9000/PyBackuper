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


def delete_if_exist(path):
    if os.path.exists(path):
        if isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)


def copy_overwrite(item, destination):
    if isfile(item):
        shutil.copyfile(item, destination)
    else:
        shutil.copytree(item, destination)


def copy_item(file_path, destination_path):
    create_dir_if_not_exist(os.path.dirname(destination_path))
    if os.path.exists(destination_path):
        delete_if_exist(destination_path)
    copy_overwrite(file_path, destination_path)


def fill_default(item):
    if 'Enabled' not in item:
        item['Enabled'] = True
    if 'InnerPath' not in item:
        item['InnerPath'] = '/'
    if 'Name' not in item:
        item['Name'] = os.path.basename(item['Path'])


def main():
    logging.basicConfig(level=logging.DEBUG)
    with open(ConfigFilePath) as json_file:
        data = json.load(json_file)
        for store_item in data['StoreItems']:
            fill_default(store_item)

            if store_item['Enabled']:
                destination_dir = os.path.join(data['RootFolder'], store_item['InnerPath'])
                copy_item(store_item['Path'], destination_dir)
                logging.info(f"{store_item['Name']} successfully stored to {store_item['InnerPath']}")


if __name__ == "__main__":
    main()
