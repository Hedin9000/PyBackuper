import os
from os.path import isfile, join
import json
import logging
import zipfile
import file_operations as fo

ConfigFilePath = 'config.json'


def copy_item(file_path, destination_path):
    fo.create_dir_if_not_exist(os.path.dirname(destination_path))
    if os.path.exists(destination_path):
        fo.delete_if_exist(destination_path)
    fo.copy_overwrite(file_path, destination_path)


def fill_default(item):
    if 'Enabled' not in item:
        item['Enabled'] = True
    if 'InnerPath' not in item:
        item['InnerPath'] = os.path.basename(item['Path'])
    if 'Name' not in item:
        item['Name'] = os.path.basename(item['Path'])
    if 'Zip' not in item:
        item['Zip'] = True
    if 'Condition' not in item:
        item['Condition'] = 'Updated'


def get_updated_datetime(path):
    if isfile(path):
        return os.path.getmtime(path)
    else:
        return max(os.path.getmtime(root) for root, _, _ in os.walk(path))


def check_condition(store_item, destination):
    condition = store_item['Condition']
    if condition == 'Always' or not os.path.exists(destination):
        return True
    item_datetime = get_updated_datetime(store_item['Path'])
    in_store_datetime = get_updated_datetime(destination)

    if item_datetime > in_store_datetime:
        return True
    else:
        logging.info(f'{store_item["Name"]} skipped (not modified)')
        return False


def pre_config():
    logging.basicConfig(format='%(asctime)s: %(levelname)s\t%(message)s', level=logging.DEBUG)
    zipfile.Z_DEFAULT_COMPRESSION = 9


def main():
    pre_config()
    with open(ConfigFilePath) as json_file:
        data = json.load(json_file)
        for store_item in data['StoreItems']:
            fill_default(store_item)

            if store_item['Enabled']:
                destination = os.path.join(data['RootFolder'], store_item['InnerPath'])

                if store_item['Zip']:
                    destination = destination + '.zip'
                    if not check_condition(store_item, destination):
                        continue
                    fo.delete_if_exist(destination)
                    fo.zip_item(store_item['Path'], destination)
                else:
                    if not check_condition(store_item, destination):
                        continue
                    copy_item(store_item['Path'], destination)
                item_size = fo.get_formatted_size(destination)
                logging.info(f"{store_item['Name']} successfully stored to {store_item['InnerPath']} ({item_size})")

    logging.info(
        f"Total size of Store: {fo.convert_size(fo.get_formatted_size(data['RootFolder']))}")


if __name__ == "__main__":
    main()
