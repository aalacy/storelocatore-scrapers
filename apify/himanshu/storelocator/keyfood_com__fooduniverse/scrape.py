import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    page = 0
    while True:
        r = session.get("https://www.keyfood.com/store/keyFood/en/store-locator?q=11756&page=" + str(page) + "&radius=5000000000&all=true",headers=headers)
        data = r.json()["data"]
        for store_data in data:
            store = []
            store.append("https://www.keyfood.com")
            store.append(store_data["displayName"])
            store.append(store_data["line1"] + " " + store_data["line2"] if store_data["line2"] else store_data["line1"])
            store.append(store_data["town"])
            store.append(store_data["state"])
            store.append(store_data["postalCode"])
            store.append("US")
            store.append(store_data["name"])
            store.append(store_data["phone"] if store_data["phone"] else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            hours = ""
            for hour in store_data["openings"]:
                hours = hours + " " + hour + store_data["openings"][hour]
            store.append(hours if hours else "<MISSING>")
            store.append("<MISSING>")
            yield store
        if len(data) < 250:
            break
        page = page + 1


def scrape():
    data = fetch_data()
    write_output(data)

scrape()