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
    base_url = "https://www.originalpenguin.com"
    r = session.get("https://api.zenlocator.com/v1/apps/app_7tx9r8kr/locations/search?northeast=67.193746%2C31.935493&southwest=-26.135222%2C-180",headers=headers)
    return_main_object = []
    location_list = r.json()["locations"]
    for i in range(len(location_list)):
            store_data = location_list[i]
            store = []
            store.append("https://www.originalpenguin.com")
            store.append(store_data["name"])
            store.append(store_data["address1"] + " " + store_data["address2"])
            store.append(store_data["city"])
            store.append(store_data["region"])
            store.append(store_data["postcode"])
            store.append(store_data["countryCode"])
            store.append("<MISSING>")
            store.append(store_data["contacts"]["con_c4g3q3jz"]["text"] if "con_c4g3q3jz" in store_data["contacts"]  != "" else "<MISSING>")
            store.append("original penguin")
            store.append(store_data["lat"])
            store.append(store_data["lng"])
            store.append(store_data["hours"] if store_data["hours"]  != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
