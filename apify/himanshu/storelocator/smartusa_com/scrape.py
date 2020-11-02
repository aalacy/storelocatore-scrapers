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
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.smartusa.com"
    r = session.get("https://www.smartusa.com/dealers/find/zipcode/11756/distance/1000000",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    location_url = []
    for store_data in r.json()["response"]["dealers"]:
        store = []
        store.append("https://www.smartusa.com")
        store.append(store_data["dealerName"])
        store.append(store_data["address"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zipCode"])
        store.append("US")
        store.append(store_data["dealerCode"])
        store.append(store_data["phone"] if store_data["phone"] != "NO PRP TEL" else "<MISSING>")
        store.append("smart usa")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
