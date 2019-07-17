import os
import sys
import csv
import json
import validator
from glob import glob

SUCCESS_FILEPATH = './SUCCESS'


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


if __name__ == "__main__":
    data = []
    data_location = sys.argv[1]
    debug = len(sys.argv) > 2 and sys.argv[2] == "DEBUG"

    if data_location.endswith(".csv"):
        with open(data_location) as csv_file:
            reader = csv.DictReader(csv_file, skipinitialspace=True)
            for row in reader:
                data.append(row)
    else:
        for f_name in glob(os.path.join(data_location, 'datasets/default', '*.json')):
            with open(f_name) as json_file:
                data.append(json.load(json_file))

    validator.validate(data, debug)
    if not debug:
        touch(SUCCESS_FILEPATH)
        with open(SUCCESS_FILEPATH, 'a') as f:
            f.write(validator.__version__)

