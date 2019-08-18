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
    base_url = "http://samssoutherneatery.com"
    r = requests.get("http://samssoutherneatery.com/wp-admin/admin-ajax.php?action=store_search&lat=0&lng=0&max_results=10000&search_radius=10000&autoload=1",headers=headers)
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("http://samssoutherneatery.com")
        store.append(store_data["store"])
        store.append(store_data["address"] + " " + store_data["address2"] if 'address2' in store_data else store_data["address"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data["id"])
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append("sam's southern eatery")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append(" ".join(list(BeautifulSoup(store_data["hours"],"lxml").stripped_strings)))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
