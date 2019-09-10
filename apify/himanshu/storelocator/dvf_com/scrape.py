import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    cords = sgzip.coords_for_radius(50)
    for cord in cords:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            "accept" : "application/json, text/javascript, */*; q=0.01",
            "x-requested-with": "XMLHttpRequest"
        }
        r = requests.get("https://www.dvf.com/on/demandware.store/Sites-DvF_US-Site/default/Stores-FinderJSON?lat=" + str(cord[0])  + "&lng=" + str(cord[1])  + "&showRP=true&showOutlet=false",headers=headers)
        data = r.json()
        for state_data in data['results']:
            for store_data in state_data["stores"]:
                store = []
                store.append("https://www.dvf.com")
                store.append(store_data["name"])
                store.append(store_data["address1"] + " " + store_data['address2'] if store_data["address2"] != None else store_data["address1"])
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(store_data["city"])
                store.append(store_data["stateCode"])
                store.append(store_data["postalCode"])
                store.append(store_data["countryCode"])
                store.append(store_data["id"])
                store.append(store_data["phone"] if store_data["phone"] != "" and store_data["phone"] != None else "<MISSING>")
                store.append("diane von furstenberg")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                hours = " ".join(list(BeautifulSoup(store_data["storeHours"],"lxml").stripped_strings))
                store.append(hours if hours != "" else "<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
