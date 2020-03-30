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
    base_url = "https://altamere.com"
    r = session.get(base_url + "/api/json/places/get")
    data = r.json()["places"]["locations"]
    return_main_object = []

    for i in range(len(data)):
        current_store = data[i]
        store = []
        store.append("https://altamere.com")
        store.append(current_store["entry"]["title"])
        store.append(current_store["postalAddress"]['street'])
        store.append(current_store["postalAddress"]['city'])
        store.append(current_store["postalAddress"]['region'])
        store.append(current_store["postalAddress"]['code'])
        store.append(current_store["postalAddress"]['country'])  
        store.append("<MISSING>")
        store.append(current_store["contacts"]['phone'])
        store.append("altamere")
        store.append(current_store["geoLocation"]["lat"])
        store.append(current_store["geoLocation"]["lng"])
        store_hours = current_store["entry"]["text"].replace("\n"," ") if current_store["entry"]["text"] else "<MISSING>"
        if "Fax:" in store_hours:
            store_hours = store_hours.split("Fax:")[0]
        store.append(store_hours if store_hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
