import csv
import requests
from bs4 import BeautifulSoup
import re
import json

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
    base_url = "https://www.zipscarwash.com"
    r = requests.get("https://zipscarwash.com/wp-admin/admin-ajax.php?action=store_search&lat=0&lng=0&max_results=1000000&radius=1000000&autoload=1",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_list = r.json()
    for store_data in location_list:
        store = []
        store.append("https://www.zipscarwash.com")
        store.append(store_data['store'])
        store.append(store_data["address"] + store_data["address2"])
        store.append(store_data['city'])
        store.append(store_data['state'])
        store.append(store_data["zip"] if store_data["zip"] != None and store_data["zip"] != "" else "<MISSING>")
        store.append("US")
        store.append(store_data["id"])
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append("zips car wash")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append(" ".join(list(BeautifulSoup(store_data["hours"],"lxml").stripped_strings)) if store_data["hours"] != None else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
