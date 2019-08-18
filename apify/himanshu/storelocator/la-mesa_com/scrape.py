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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://la-mesa.com"
    r = requests.get("https://la-mesa.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    geo_object = {}
    for location in soup.find_all("div",{'class':"et_pb_map_pin"}):
        location_details = list(location.stripped_strings)
        if "@" in location_details[-1]:
            del location_details[-1]
        if "Fax" in location_details[-1]:
            del location_details[-1]
        store = []
        store.append("https://la-mesa.com")
        store.append(location_details[0])
        if len(location_details[3].split(",")) == 2:
            store.append(location_details[2])
            store.append(location_details[3].split(",")[0])
            store.append(location_details[3].split(",")[-1].split(" ")[-2])
            store.append(location_details[3].split(",")[-1].split(" ")[-1])
        else:
            store.append(location_details[0])
            store.append(" ".join(location_details[2].split(",")[0].split(" ")[:-2]))
            store.append(location_details[2].split(",")[-1].split(" ")[-2])
            store.append(location_details[2].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[-1])
        store.append(location_details[1])
        store.append(location["data-lat"])
        store.append(location["data-lng"])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
