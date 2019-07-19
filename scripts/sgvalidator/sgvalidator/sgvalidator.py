import os
import csv
import json
import termcolor
from glob import glob
from .validator_utils import ValidatorUtils
from .data_checker import DataChecker

# make sure this is the same as in setup.py
VERSION = "0.0.9"
SUCCESS_FILEPATH = './SUCCESS'


def validate(data_location, debug=False):
    data = _readDataFromLocation(data_location, debug)
    _validate(data, debug)
    if not debug:
        _touch(SUCCESS_FILEPATH)
        with open(SUCCESS_FILEPATH, 'a') as f:
            f.write(VERSION)


def _readDataFromLocation(data_location, debug):
    data = []
    if data_location.endswith(".csv"):
        with open(data_location) as csv_file:
            reader = csv.DictReader(csv_file, skipinitialspace=True)
            for row in reader:
                data.append(row)
    else:
        for f_name in glob(os.path.join(data_location, 'datasets/default', '*.json')):
            with open(f_name) as json_file:
                data.append(json.load(json_file))

    if len(data) == 0:
        ValidatorUtils.fail("Data location {} doesn't exist or dataset is empty!".format(data_location), debug)

    return data


def _touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def _validate(data, debug):
    print(termcolor.colored("Validating data with DEBUG = {}".format(debug), "green"))
    checks = DataChecker(data, debug)
    checks.check_data()
