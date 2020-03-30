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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    "Content-Type": "application/json; charset=UTF-8"
    }
    base_url = "https://racetrac.com"
    data = '{"swLat":25.82303640133416,"swLng":-115.6947670532553,"neLat":41.79048379771046,"neLng":-61.202579553255305,"features":[]}'
    r = session.post("https://racetrac.com/Services.asmx/Locate",headers=headers,data=data)
    return_main_object = []
    location_list = r.json()
    store_ids = []
    for key in location_list:
        if "Stores" in location_list[key]:
            for store_data in location_list[key]["Stores"]:
                store = []
                store.append("https://racetrac.com")
                store.append("<MISSING>")
                store.append(store_data["Address"])
                store.append(store_data['City'])
                store.append(store_data['State'])
                store.append(store_data["ZipCode"])
                store.append("US")
                store.append(store_data["StoreNumber"])
                if store[-1] in store_ids:
                    continue
                store_ids.append(store[-1])
                store.append(store_data["PhoneNumber"].split("x")[0] if store_data["PhoneNumber"] else "<MISSING>")
                store.append("<MISSING>")
                store.append(store_data["Latitude"] if store_data["Latitude"] != 0 else "<MISSING>")
                store.append(store_data["Longitude"] if store_data["Longitude"] != 0 else "<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
