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
    base_url = "https://www.millenniumhotels.com"
    r = session.get("https://www.millenniumhotels.com/api/data/destinations",headers=headers)
    return_main_object = []
    for store_data in r.json():
        if "United States" not in store_data["address"]:
            continue
        location_request = session.get(base_url + store_data["url"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        store = []
        store.append("https://www.millenniumhotels.com")
        store.append(store_data["name"])
        address = store_data["address"]
        for i in range(len(address.split(" "))):
            if len(address.split(" ")[i].replace(",","")) == 2 and address.split(" ")[i].replace(",","").isdigit() == False:
                state = address.split(" ")[i]
        for i in range(len(address.split(" "))):
            if len(address.split(" ")[i].replace(",","")) == 5 and address.split(" ")[i].replace(",","").isdigit():
                store_zip = address.split(" ")[i]
        address = address.split(state)[0][:-2]
        if len(address.split(",")) == 2:
            store.append(address.split(",")[0])
            store.append(address.split(",")[1])
        else:
            store.append(" ".join(address.split(" ")[:-1]))
            store.append(address.split(" ")[-1])
        store.append(state.replace(",",""))
        store.append(store_zip.replace(",",""))
        store.append("US")
        store.append(store_data["hotelid"])
        store.append(store_data["telphone"])
        store.append("millennium hotels")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
