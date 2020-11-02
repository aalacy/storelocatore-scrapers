import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://donutconnection.com"
    r = session.post(base_url + "/wp-content/plugins/store-locator/sl-xml.php")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for store_data in soup.find_all("marker"):
        store = []
        store.append("https://donutconnection.com")
        store.append(store_data['name'])
        store.append(store_data["street"] if store_data["street"] != "" else "<MISSING>")
        store.append(store_data['city'])
        store.append(store_data['state'])
        store.append(store_data["zip"].strip())
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data['phone'] if store_data['phone'] != "" else "<MISSING>")
        store.append("donut connection")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
