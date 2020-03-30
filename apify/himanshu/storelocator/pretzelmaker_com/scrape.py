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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    "content-type": "application/x-www-form-urlencoded"
    }
    base_url = "https://pretzelmaker.com"
    data = "locateStore=true&country=USA&latitude=21.2099072&longitude=72.84736"
    r = session.post("https://pretzelmaker.com/locations/",headers=headers,data=data)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if 'var stores = ' in script.text:
            location_list = json.loads(script.text.split("var stores = ")[1].split("}];")[0] + "}]")
            for store_data in location_list:
                store = []
                store.append("https://pretzelmaker.com")
                store.append(store_data['sl_name'])
                store.append(store_data["sl_address"])
                store.append(store_data['sl_city'])
                store.append(store_data['sl_state'])
                store.append(store_data["sl_zip"])
                store.append("US")
                store.append(store_data["sl_id"])
                store.append(store_data["sl_phone"] if store_data["sl_phone"] != "*" and store_data["sl_phone"] != "TBD" else "<MISSING>")
                store.append("pretzel maker")
                store.append(store_data["sl_latitude"])
                store.append(store_data["sl_longitude"])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
