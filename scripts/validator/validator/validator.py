import os
import sys
import csv
import json
import termcolor
import validator
from glob import glob
from .datachecker import DataChecker

SUCCESS_FILEPATH = './SUCCESS'

def validate():
    data, debug = __readDataAndDebug()
    __validate(data, debug)
    if not debug:
        __touch(SUCCESS_FILEPATH)
        with open(SUCCESS_FILEPATH, 'a') as f:
            f.write(validator.__version__)

def __readDataAndDebug():
    data = []
    try:
        data_location = sys.argv[1]
    except IndexError:
        print("Please include a data location!")
        exit(0)

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

    return (data, debug)

def __touch(path):
    with open(path, 'a'):
        os.utime(path, None)

def __validate(data, debug):
    print(termcolor.colored("Validating data...", "green"))
    checks = DataChecker(data, debug)
    checks.check_data()
