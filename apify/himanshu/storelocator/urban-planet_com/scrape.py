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
    base_url = "https://urban-planet.com"
    r = session.get("https://urban-planet.com/apps/api/v1/stores?location%5Blongitude%5D=-74.0059728&location%5Blatitude%5D=40.7127753&location%5Bradius%5D=1000000&location%5Bunits%5D=km&_=1564147491195")
    data = r.json()["stores"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://urban-planet.com")
        store.append(store_data["address"]['name'])
        if store_data["address"]["line2"] == None:
            store_data["address"]["line2"] = ""
        if store_data["address"]["line3"] == None:
            store_data["address"]["line3"] = ""
        store.append(store_data["address"]["line1"] + store_data["address"]["line2"] + store_data["address"]["line3"])
        store.append(store_data["address"]["city"])
        store.append(store_data["address"]["state"])
        store.append(store_data["address"]["zip"])
        store.append(store_data["address"]["country_code"])
        store.append(store_data["store_code"])
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append(store_data["brand"])
        store.append(store_data["address"]['latitude'])
        store.append(store_data["address"]['longitude'])
        store_hours = store_data["open_hours"]
        hours = ""
        for k in range(len(store_hours)):
            hours = hours + " " + store_hours[k]["day"] + " open time " + store_hours[k]["open_time"] + " close time " + store_hours[k]["close_time"]
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
