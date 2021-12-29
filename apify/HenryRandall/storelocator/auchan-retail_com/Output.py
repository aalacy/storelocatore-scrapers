import os
import csv
import json


def fetch_data():
    base = os.getcwd()
    base = os.path.join(base, "apify_docker_storage;C", "datasets", "default")
    files = os.listdir(base)
    data = []

    for file in files:
        path = os.path.join(base, file)
        with open(path, "r") as location:
            location_data = list(json.load(location).values())
            data.append(location_data)
        with open(path, "r") as location:
            keys = list(json.load(location).keys())
    return data, keys


def write_output(data, keys):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(keys)

        for row in data:
            writer.writerow(row)


def scrape():
    data, keys = fetch_data()
    write_output(data, keys)


scrape()
