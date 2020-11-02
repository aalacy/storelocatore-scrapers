import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    base_url = "https://www.miniusa.com"
    r = session.post("https://www.miniusa.com/api/dealer/dealerLookup.action?offeringtypes=N&returnall=true&zip=50108",headers=headers)
    data = r.json()
    return_main_object = []
    for store_data in data:
        store = []
        store.append("https://www.miniusa.com")
        store.append(store_data["name"])
        store.append(store_data["street"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data["center_code"])
        store.append(store_data["phone"])
        store.append("mini usa")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        store.append("<INACCESSIBLE>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()