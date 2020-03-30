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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://apoyo-financiero.com"
    r = session.post(base_url + "/sucursales.json")
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("http://apoyo-financiero.com")
        store.append(store_data['name'])
        print(store_data['address'])
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        if len(store_data['address'].split(",")[-1].split(" ")) == 4:
            store.append(store_data['address'].split(",")[-1].split(" ")[-3])
            store.append(store_data["address"].split(",")[-1].split(" ")[-1])
        else:
            store.append(store_data['address'].split(",")[-1].split(" ")[-2])
            store.append(store_data["address"].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data['tel'])
        store.append("apoyo financiero")
        store.append(store_data["lat"])
        store.append(store_data["lon"])
        store.append("<MISSING>")
        store.append(store_data['address'].split(",")[0])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
