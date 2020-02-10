import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://www.oribe.com"
    r = requests.get("https://www.oribe.com/locator/ajax/storelocator/brand/Oribe",headers=headers)
    data = r.json()["data"]
    return_main_object = []
    addresses = []
    for store_data in data:
        if store_data["country"] != "United States" and store_data["country"] != "Canada":
            continue
        store = []
        store.append("https://www.oribe.com")
        store.append(store_data["name"])
        store[-1] = re.sub('[^0-9a-zA-Z < >]', ' ', store[-1])
        store.append(store_data["addr1"] + " " + store_data["addr2"] if store_data["addr2"] != None else store_data["addr1"])
        store[-1] = re.sub('[^0-9a-zA-Z < > &]', ' ', store[-1])
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])
        store.append(store_data["city"])
        store[-1] = re.sub('[^0-9a-zA-Z < >]', ' ', store[-1])
        store.append(store_data["state"])
        store[-1] = re.sub('[^0-9a-zA-Z < >]', ' ', str(store[-1]))
        store.append(store_data["postal_code"])
        store.append("US" if store_data["country"] == "United States" else "CA")
        store.append(store_data["id"])
        store.append(store_data["phone"].split("Ext")[0] if store_data["phone"] != None and store_data["phone"] != "" else "<MISSING>")
        store[-1] = re.sub('[^0-9a-zA-Z < > ( )]', ' ', store[-1])
        store.append("oribe")
        store.append(store_data['latitude'])
        store.append(store_data['longitude'])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
