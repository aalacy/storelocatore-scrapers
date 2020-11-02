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
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    data = "ajax=1&action=get_nearby_stores&distance=20000000000&lat=38.7745565&lng=-75.13934979999999"
    base_url = "https://www.papayaclothing.com"
    r = session.post("https://www.papayaclothing.com/cms/papaya_store.aspx",headers=headers,data=data)
    return_main_object = []
    location_list = r.json()["stores"]
    for i in range(len(location_list)):
        store_data = location_list[i]
        store = []
        store.append("https://www.papayaclothing.com")
        store.append(store_data["name"])
        if "(opening" in store[-1]:
            continue
        store.append(store_data["address1"] + store_data["address2"] if "address2" in store_data and store_data["address2"] != None else store_data["address1"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zipcode"] if store_data["zipcode"] else '<MISSING>')
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["telephone"] if store_data["telephone"] else "<MISSING>")
        store.append("papaya")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append("<MISSING>")
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
