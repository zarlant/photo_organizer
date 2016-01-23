import os
import exifread
from shutil import copyfile

# source_directory = "Z:\\Temp"
# destination_directory = "Z:\\TempDestTest"
source_directory = "F:\\Pictures"
destination_directory = "Y:\\Photos"

def update_date_data(filename, date, date_dict):
    date_parts = date.split(" ")
    if len(date_parts) > 1:
        date_only = date_parts[0].split(":")
        if len(date_only) == 3:
            year = date_only[0]
            month = date_only[1]
            day = date_only[2]
            datestring = "%s-%s-%s" % (year, month, day)
            if year not in date_dict:
                date_dict[year] = {}

            if datestring not in date_dict[year]:
                date_dict[year][datestring] = []
            date_dict[year][datestring].append(filename)
            return date_dict
        else:
            date_dict["unknown"].append(filename)
            return date_dict
    else:
        date_dict["unknown"].append(filename)
        return date_dict


def create_and_copy(directory_path, directory_key, destination_directory, data):
    full_dest_path = os.path.join(destination_directory, directory_path)
    if not os.path.exists(full_dest_path) and len(data[directory_key]) > 0:
        os.makedirs(full_dest_path)
    for current_file in data[directory_key]:
        copyfile(current_file, os.path.join(full_dest_path, os.path.basename(current_file)))


def walk_directories(current_data, directory_keys):
    for directory_key in current_data:
        current_type = type(current_data[directory_key])
        if current_type == list:
            dir_path = ""
            if len(directory_keys) > 0:
                for directory in directory_keys:
                    dir_path = os.path.join(dir_path, directory)

            dir_path = os.path.join(dir_path, directory_key)
            create_and_copy(dir_path, directory_key, destination_directory, current_data)
        elif current_type == dict:
            directory_keys.append(directory_key)
            walk_directories(current_data[directory_key], directory_keys)
            directory_keys = []


date_data = {"unknown": []}
full_file = None
count = 0
for root, directories, filenames in os.walk(source_directory):
    for file in filenames:
        if file.endswith("jpg") or file.endswith("JPG") or file.endswith("bmp"):
            count += 1
            try:
                full_file = os.path.join(root, file)
                with open(full_file, 'rb') as img:
                    tags = exifread.process_file(img)
                    if "EXIF DateTimeOriginal" in tags:
                        date_info = tags["EXIF DateTimeOriginal"]
                        if date_info == "EXIF DateTimeOriginal":
                            date_data["unknown"].append(full_file)
                        date_data = update_date_data(full_file, date_info.printable, date_data)
                        print "------------"
                        print full_file
                        print tags["EXIF DateTimeOriginal"]
                        print "------------"
                    else:
                        date_data["unknown"].append(full_file)
            except Exception as err:
                print err

print date_data
print "Collected %s files." % count

walk_directories(date_data, [])