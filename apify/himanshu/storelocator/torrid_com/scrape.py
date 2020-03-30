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
    base_url = "https://www.torrid.com"
    r = session.get("https://www.torrid.com/on/demandware.store/Sites-torrid-Site/default/Stores-GetNearestStores?postalCode=11756&customStateCode=&maxdistance=10000000&unit=mi&latitude=40.7226698&longitude=-73.51818329999998&maxResults=15&distanceUnit=mi&countryCode=US&counter=1000000000",headers=headers)
    data = r.json()["stores"]
    return_main_object = []
    for key in data:
        store_data = data[key]
        store = []
        store.append("https://www.torrid.com")
        store.append(store_data['name'])
        store.append(store_data["address1"] + " " + store_data["address2"] if store_data["address2"] != None else store_data["address1"])
        store.append(store_data['city'])
        store.append(store_data['stateCode'])
        store.append(store_data["postalCode"])
        store.append(store_data["countryCode"])
        store.append(key)
        store.append(store_data["phone"])
        store.append("torrid")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        store.append(" ".join(list(BeautifulSoup(store_data["storeHours"],"lxml").stripped_strings)) if store_data["storeHours"] != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
