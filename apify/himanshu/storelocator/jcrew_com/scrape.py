import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    r = session.get("https://stores.jcrew.com/en/api/v2/stores.json",headers=headers)
    data = r.json()['stores']
    for store_data in data:
        if store_data["country_code"] not in ("US","CA"):
            continue
        store = []
        store.append("https://www.jcrew.com")
        store.append(store_data["name"])
        store.append(store_data["address_1"] + " " + store_data["address_2"] if store_data['address_2'] else store_data['address_1'])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["postal_code"])
        store.append(store_data["country_code"])
        if store[-1] == "CA":
            ca_zip_split = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',store[-2])
            if ca_zip_split:
                store[-2] = ca_zip_split[-1]
        store.append(store_data["id"])
        store.append(store_data["phone_number"] if store_data["phone_number"] else "<MISSING>")
        store.append("<MISSING>")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        for hours_details in store_data["regular_hour_ranges"]:
            hours = hours + " " + hours_details["days"] + " " + hours_details["hours"]
        store.append(hours if hours else "<MISSING>")
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = store[i].replace("–","-").replace("&#8211;","-")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()