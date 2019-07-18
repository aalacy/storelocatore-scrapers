import os
import csv


def getFakeData(fname='sample_data_good_header.csv'):
    data = []
    path = os.path.join(os.path.dirname(__file__), fname)
    with open(path) as csv_file:
        reader = csv.DictReader(csv_file, skipinitialspace=True)
        for row in reader:
            data.append(row)
    return data