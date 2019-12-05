import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.lillypulitzer.com"
    r = requests.get("https://www.lillypulitzer.com/on/demandware.store/Sites-lillypulitzer-us-Site/default/Stores-GetNearestStores?latitude=37.751&longitude=-97.822&countryCode=US&distanceUnit=mi&maxdistance=10000", headers=headers)
    data = r.json()["stores"]
    return_main_object = []
    for key in data:
        store_data = data[key]
        store = []

        if "Lilly" in store_data['storeType']:
            location_type = store_data['storeType']
        else:
            location_type = "Other Lilly Destinations"

        store.append("https://www.lillypulitzer.com")
        store.append(store_data["name"])
        store.append(store_data["address1"] + " " + store_data["address2"])
        store.append(store_data["city"])
        store.append(store_data["stateCode"])
        if len(store_data["stateCode"]) > 2:
            continue
        if store[-1] == "ZZ":
            store[-1] = store_data["city"].split(",")[1]
            store[-2] = store_data["city"].split(",")[0]
        store.append(store_data["postalCode"]
                     if store_data["postalCode"] != "" else "<MISSING>")
        store.append(store_data["countryCode"])
        if len(store_data["postalCode"]) == 7:
            store[-1] = "CA"
        if store[-1] == "":
            store[-1] = "US"
        store.append("<MISSING>")
        store.append(store_data["phone"]
                     if store_data["phone"] != "" else "<MISSING>")
        store.append(location_type)
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        store_hours = store_data["storeHours"]
        for key in store_hours:
            hours = hours + " " + key + " " + store_hours[key]
        store.append(hours if hours != "" else "<MISSING>")
        store.append(store_data['storeUrl']
                     if store_data['storeUrl'] != '' else "<MISSING>")
        return_main_object.append(store)
        #print("===" + str(store))
        #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
