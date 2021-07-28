import pandas as pd
import os
import csv
import json

def fetch_data():
    basepath = os.getcwd()
    basepath = os.path.join(basepath, 'apify_docker_storage;C', 'datasets', 'default')
    files = os.listdir(basepath)
    data = []

    for file in files:
        path = os.path.join(basepath, file)
        with open(path, 'r') as location:
            location_data = list(json.load(location).values())
            data.append(location_data)
    return data

def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        for row in data:
            writer.writerow(row)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()