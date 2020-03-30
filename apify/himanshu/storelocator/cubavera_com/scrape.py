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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://www.cubavera.com"
    r = session.get("https://api.zenlocator.com/v1/apps/app_txdmatvw/locations/search?northeast=77.064637%2C149.5221&southwest=-57.442352%2C-180",headers=headers)
    data = r.json()["locations"]
    return_main_object = []
    for store_data in data:
        if "coming soon" in store_data["address"].lower():
            continue
        store = []
        store.append("https://www.cubavera.com")
        store.append(store_data["name"])
        if store_data['address'] == "":
            store.append(store_data["address1"] + " " + store_data["address2"])
        else:
            store.append(" ".join(store_data["address"].split(",")[:-2]).replace("\n"," "))
        store.append(store_data["city"])
        if store[-1] == "":
            store[-1] = store_data["visibleAddress"].split(",")[1]
        store.append(store_data["region"])
        store.append(store_data["postcode"] if store_data["postcode"] != "" else "<MISSING>")
        if store[-1] == "<MISSING>":
            store[-1] = store_data["address"].split(" ")[-1]
        store.append(store_data["countryCode"])
        store.append("<MISSING>")
        store.append(store_data["contacts"]["con_ha9dqw4s"]["text"] if "con_ha9dqw4s" in store_data["contacts"] else "<MISSING>")
        store.append("cubavera")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        hours = ""
        if store_data["hours"] == "":
            store.append("<MISSING>")
        else:
            store_hours = store_data["hours"]["hoursOfOperation"]
            for key in store_hours:
                hours = hours + " " + key + " " + store_hours[key]
            store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
