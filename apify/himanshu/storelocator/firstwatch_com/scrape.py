import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.firstwatch.com"
    r = requests.get( base_url + "/api/get_locations.php?latitude=40.72435088183902&longitude=-73.99567694507842")
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.firstwatch.com")
        store.append(store_data['name'])
        store.append(store_data["address"])
        store.append(store_data['city'])
        store.append(store_data['state'])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data["id"])
        store.append(store_data["phone"])
        store.append("emory healthcare")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        store.append("<INACCESSIBLE>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
