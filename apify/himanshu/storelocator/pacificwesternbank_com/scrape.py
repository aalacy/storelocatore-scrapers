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
    base_url = "https://www.pacificwesternbank.com"
    r = session.post("https://www.pacwest.com/api/locations",headers=headers)
    return_main_object = []
    location_list = r.json()
    for i in range(len(location_list)):
        store_data = location_list[i]
        store = []
        store.append("https://www.pacificwesternbank.com")
        store.append(store_data["name"])
        store.append(store_data["street"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data["id"])
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append("pacific western bank " + store_data["type"][0])
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        hours = ""
        store_hours = store_data["hours"]
        for k in range(len(store_hours)):
            hours = hours + " " + store_hours[k]["day"] + " " + store_hours[k]["time"]
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
