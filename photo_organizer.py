import os
import exifread
from shutil import copyfile
import argparse
import random

# source_directory = "Z:\\Temp"
# destination_directory = "Z:\\TempDestTest"
# source_directory = "F:\\Pictures"
# destination_directory = "Y:\\Photos"


class PhotoOrganizer(object):
    def __init__(self, source, destination):
        self.FILE_EXTENSIONS = [".jpg", ".jpeg", ".cr2", ".png", ".avi", ".mov"]
        self.processed_count = 0
        self.source_directory = source
        self.destination_directory = destination

    def update_date_data(self, filename, date, date_dict):
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

    def walk_directories(self, current_data, directory_keys):
        for directory_key in current_data:
            current_type = type(current_data[directory_key])
            if current_type == list:
                dir_path = ""
                if len(directory_keys) > 0:
                    for directory in directory_keys:
                        dir_path = os.path.join(dir_path, directory)

                dir_path = os.path.join(dir_path, directory_key)
                self.create_and_copy(dir_path, directory_key, destination_directory, current_data)
            elif current_type == dict:
                directory_keys.append(directory_key)
                self.walk_directories(current_data[directory_key], directory_keys)
                directory_keys = []

    def create_and_copy(self, directory_path, directory_key, destination, data):
        full_dest_path = os.path.join(destination, directory_path)
        if not os.path.exists(full_dest_path) and len(data[directory_key]) > 0:
            os.makedirs(full_dest_path)
        for current in data[directory_key]:
            dest_base = os.path.basename(current)
            #TODO: Write MD5 check here.
            if os.path.exists(os.path.join(full_dest_path, dest_base)):
                copyfile(current, os.path.join(full_dest_path, str(random.random()) + "_" + dest_base))
            else:
                copyfile(current, os.path.join(full_dest_path, dest_base))
            self.processed_count += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help="Directory to collect photos from.", required=True)
    parser.add_argument("-d", "--destination", help="Directory to copy organized files to.", required=True)
    args = parser.parse_args()
    source_directory = str(args.source)
    destination_directory = str(args.destination)
    organizer = PhotoOrganizer(source_directory, destination_directory)

    date_data = {"unknown": []}
    full_file = None
    count = 0
    for root, directories, filenames in os.walk(source_directory):
        for current_file in filenames:
            f_name, f_ext = os.path.splitext(current_file)
            if f_ext.lower() in organizer.FILE_EXTENSIONS:
                count += 1
                try:
                    full_file = os.path.join(root, current_file)
                    with open(full_file, 'rb') as img:
                        tags = exifread.process_file(img, stop_tag='DateTimeOriginal', details=False)
                        if "EXIF DateTimeOriginal" in tags:
                            date_info = tags["EXIF DateTimeOriginal"]
                            if date_info == "EXIF DateTimeOriginal":
                                date_data["unknown"].append(full_file)
                            date_data = organizer.update_date_data(full_file, date_info.printable, date_data)
                        else:
                            date_data["unknown"].append(full_file)
                except Exception as err:
                    print err

    print "Collected %s files." % count

    organizer.walk_directories(date_data, [])

    print "Processed %s files." % organizer.processed_count