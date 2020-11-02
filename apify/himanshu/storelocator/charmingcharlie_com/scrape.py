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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.charmingcharlie.com"
    r = session.get("https://www.charmingcharlie.com/stores",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    addresses = []
    for script in soup.find_all("script"):
        if "window.storeData = " in script.text:
            location_list = json.loads(script.text.split("window.storeData = ")[1].split("};")[0] + "}")["stores"]
            for store_data in location_list:
                store = []
                store.append("https://www.charmingcharlie.com")
                store.append(store_data["name"])
                store.append(store_data["address1"] + " " + store_data["address2"])
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(store_data["city"])
                store.append(store_data["stateCode"])
                store.append(store_data["postal"])
                store.append(store_data["countryCode"])
                store.append(store_data["ID"])
                store.append(store_data["phone"])
                store.append("charming charlie")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                store.append(" ".join(list(BeautifulSoup(store_data["storeHours"],"lxml").stripped_strings)))
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
