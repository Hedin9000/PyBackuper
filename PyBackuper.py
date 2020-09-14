import json
import logging
import zipfile
from backuper_types import StoreItem, StoreMode, ConditionMode
import os
import shutil
import math
from os.path import isfile

SizeNames = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

ConfigFilePath = 'config.json'


def get_updated_datetime(path):
    if isfile(path):
        return os.path.getmtime(path)
    else:
        return max(os.path.getmtime(root) for root, _, _ in os.walk(path))


def check_condition(data, store_item):
    destination = get_destination(data['RootFolder'], store_item)

    if store_item.Condition == ConditionMode.Always or not os.path.exists(destination):
        return True
    item_datetime = get_updated_datetime(store_item.Path)
    in_store_datetime = get_updated_datetime(destination)

    if item_datetime > in_store_datetime:
        return True
    else:
        logging.info(f'{store_item.Name} skipped (not modified)')
        return False


def create_dir_if_not_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)


def delete_if_exist(path):
    if os.path.exists(path):
        if isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)


def get_formatted_size(path):
    return convert_size(get_size(path))


def get_size(start_path):
    if isfile(start_path):
        return os.path.getsize(start_path)

    total_size = 0
    for dir_path, dir_names, file_names in os.walk(start_path):
        for f in file_names:
            fp = os.path.join(dir_path, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    result = f"{s} {SizeNames[i]}"
    return result


def pre_config():
    logging.basicConfig(format='%(asctime)s: %(levelname)s\t%(message)s', level=logging.DEBUG)
    zipfile.Z_DEFAULT_COMPRESSION = 9


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def copy_data(store_item, destination):
    item = store_item.Path
    if isfile(item):
        shutil.copyfile(item, destination)
    else:
        shutil.copytree(item, destination)


def zip_data(store_item, destination):
    item = store_item.Path
    create_dir_if_not_exist(os.path.dirname(destination))
    zipf = zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED)
    if isfile(item):
        zipf.write(item, os.path.basename(item))
    else:
        for root, dirs, files in os.walk(item):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.join(remove_prefix(root, item), file))
    zipf.close()


def get_destination(root_path, store_item):
    destination = os.path.join(root_path, store_item.InnerPath)
    if store_item.Mode == StoreMode.Zip:
        return destination + '.zip'
    elif store_item.Mode == StoreMode.Encrypt:
        return destination + '.enc'
    return destination


def main():
    pre_config()
    with open(ConfigFilePath) as json_file:
        data = json.load(json_file)
        for item in data['StoreItems']:
            store_item = StoreItem(item)

            if store_item.Enabled and check_condition(data, store_item):
                destination = get_destination(data['RootFolder'], store_item)

                create_dir_if_not_exist(os.path.dirname(destination))
                delete_if_exist(destination)

                mode_selector = {
                    StoreMode.Copy: copy_data,
                    StoreMode.Zip: zip_data
                }

                mode_selector[store_item.Mode](store_item, destination)

                item_size = get_formatted_size(destination)
                logging.info(f"{store_item.Name} successfully stored to {store_item.InnerPath} ({item_size})")

    logging.info(
        f"Total size of Store: {get_formatted_size(data['RootFolder'])}")


if __name__ == "__main__":
    main()
