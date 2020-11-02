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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://shred415.com"
    r = session.get("https://shred415.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "window.__NUXT__=" in script.text:
            location_list = json.loads(script.text.split("window.__NUXT__=")[1].split("};")[0] + "}")["data"][0]["locations"]
            for store_data in location_list:
                if "Coming Soon".lower() in store_data["stageText"].lower():
                    continue
                store = []
                store.append("https://shred415.com")
                store.append(store_data['name'])
                store.append(store_data["street1"] + " " + store_data["street2"] if store_data["street2"].split(" ")[-1] != store_data["zip"] else store_data["street1"])
                store.append(store_data['city'])
                store.append(store_data['state'])
                store.append(store_data["zip"])
                store.append("US")
                store.append(store_data["id"])
                store.append(store_data["phone"].replace("\u202d","").replace("\u200d","") if store_data["phone"] != "" else "<MISSING>")
                store.append("<MISSING>")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                store.append("<MISSING>")
                store.append("https://shred415.com/locations")
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
