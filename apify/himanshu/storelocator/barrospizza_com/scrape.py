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
    base_url = "https://barrospizza.com"
    r = session.get("https://barrospizza.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "window.__NUXT__=" in script.text:
            location_list = json.loads(script.text.split("window.__NUXT__=")[1].split("};")[0] + "}")["data"][0]["allLocations"]
    for key in location_list:
        store_data = location_list[key]
        store = []
        store.append("https://barrospizza.com")
        store.append(store_data["title"]["rendered"])
        store.append(store_data["acf"]["address"]["address_1"] + " " + store_data["acf"]["address"]["address_2"] )
        store.append(store_data["acf"]["address"]["city"])
        store.append(store_data["acf"]["address"]["state"])
        store.append(store_data["acf"]["address"]["zip"])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["acf"]["phone"])
        store.append("barro's pizzza")
        store.append(store_data["acf"]["latitude"])
        store.append(store_data["acf"]["longitude"])
        hours = ""
        for key in store_data["acf"]:
            if "hours" in key:
                hours = hours + " " + key + " " + store_data["acf"][key]
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
