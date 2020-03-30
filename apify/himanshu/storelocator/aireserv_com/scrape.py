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
    base_url = "https://www.aireserv.com"
    r = session.get(base_url + "/locations/?CallAjax=GetLocations")
    return_main_object = []
    data = r.json()
    for i in range(len(data)):
        store_data = data[i]
        if store_data['Country'] == "USA":
            store = []
            store.append("https://www.aireserv.com")
            store.append(store_data['FriendlyName'])
            store.append(store_data["Address1"])
            store.append(store_data["City"])
            store.append(store_data["State"])
            store.append(store_data["ZipCode"].strip())
            store.append("US")
            store.append(store_data['FranchiseLocationID'])
            store.append(store_data['Phone'])
            store.append("airserve")
            store.append(store_data["Latitude"])
            store.append(store_data["Longitude"])
            store.append(store_data['LocationHours'] if store_data['LocationHours'] else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

