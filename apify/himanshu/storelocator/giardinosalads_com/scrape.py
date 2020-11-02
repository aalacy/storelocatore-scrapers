import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://giardinosalads.com"
    r = session.get("https://giardinosalads.com/data/locations.json",headers=headers)
    data = r.json()["stores"]
    data = sorted(data, key=lambda k: k['title'])
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://giardinosalads.com")
        store.append(store_data["title"])
        store.append(store_data["address1"])
        store.append(store_data["address2"].split(",")[0])
        store.append(store_data["address2"].split(",")[1].split(" ")[-2])
        store.append(store_data["address2"].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append("giardino")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        hours = ""
        hour_i = 1
        while "hours" + str(hour_i) in store_data:
            hours = hours + " " + store_data["hours" + str(hour_i)]
            hour_i = hour_i + 1
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
