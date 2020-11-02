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
    r = session.get("https://www.mckinnonsmarkets.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for script in soup.find_all("script"):
        if "var locations = " in script.text:
            location_list = json.loads(script.text.split("var locations = ")[1].split("];")[0] + "]")
            for location in location_list:
                store = []
                store.append("https://www.mckinnonsmarkets.com")
                store.append(location["name"])
                store.append(location["address1"] + " " + location["address2"] if "address2" in location else location["address1"])
                store.append(location["city"])
                store.append(location["state"])
                store.append(location["zipCode"])
                store.append("US")
                store.append(location["storeID"])
                store.append(location["phone"] if location["phone"] else "<MISSING>")
                store.append("<MISSING>")
                store.append(location["latitude"])
                store.append(location["longitude"])
                store.append(location["hourInfo"].replace("\n"," ") if location["hourInfo"] else "<MISSING>")
                store.append("https://www.mckinnonsmarkets.com/locations/")
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()