import os
import shutil
import math
from os.path import isfile, join
import json
import logging
import zipfile

ConfigFilePath = 'config.json'


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


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
    if 'Zip' not in item:
        item['Zip'] = False


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def zip_item(item, zip_path):
    create_dir_if_not_exist(os.path.dirname(zip_path))

    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

    if isfile(item):
        zipf.write(item, os.path.basename(item))
    else:
        for root, dirs, files in os.walk(item):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.join(remove_prefix(root, item), file))
    zipf.close()


def get_size(start_path):
    if isfile(start_path):
        return os.path.getsize(start_path)

    total_size = 0
    for dir_path, dir_names, file_names in os.walk(start_path):
        for f in file_names:
            fp = os.path.join(dir_path, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def main():
    logging.basicConfig(format='%(asctime)s: %(levelname)s\t%(message)s', level=logging.DEBUG)
    zipfile.Z_DEFAULT_COMPRESSION = 9
    total_size = 0
    with open(ConfigFilePath) as json_file:
        data = json.load(json_file)
        for store_item in data['StoreItems']:
            fill_default(store_item)

            if store_item['Enabled']:
                destination = os.path.join(data['RootFolder'], store_item['InnerPath'])

                if store_item['Zip']:
                    destination = destination + '.zip'
                    delete_if_exist(destination)
                    zip_item(store_item['Path'], destination)
                else:
                    copy_item(store_item['Path'], destination)
                item_size = get_size(destination)
                total_size += item_size
                logging.info(
                    f"{store_item['Name']} successfully stored to {store_item['InnerPath']} ({convert_size(item_size)})")

    logging.info(f"Total size of Store: {convert_size(total_size)}")


if __name__ == "__main__":
    main()
