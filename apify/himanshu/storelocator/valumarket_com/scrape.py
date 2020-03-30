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
    page = 1
    r = session.get("https://api.freshop.com/1/stores?app_key=valu_market&has_address=true&limit=-1",headers=headers)
    location_list = r.json()["items"]
    for location in location_list:
        store = []
        store.append("https://www.valumarket.com")
        store.append(location["name"])
        store.append(location["address_1"] + " " + location["address_2"] if "address_2" in location else location["address_1"])
        store.append(location["city"])
        store.append(location["state"])
        store.append(location["postal_code"])
        store.append("US")
        store.append(location["id"])
        phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),location["phone"])
        store.append(phone[0] if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(location["latitude"])
        store.append(location["longitude"])
        store.append(location["hours_md"].replace("\n"," ") if location["hours_md"] else "<MISSING>")
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()