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
    base_url = "https://www.districttaco.com"
    r = requests.get("https://www.districttaco.com/pages/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    geo_locations = []
    for script in soup.find_all("script"):
        if "function initMap() {" in script.text:
            geo = script.text.split("lat: ")[1:]
            for lat in geo:
                geo_locations.append([lat.split(",")[0],lat.split("lng: ")[1].split("}")[0]])
        if "openingHours" in script.text:
            location_list = json.loads(script.text)["location"]
    for i in range(len(location_list)):
        store_data = location_list[i]
        store = []
        store.append("https://www.districttaco.com")
        store.append(store_data["name"])
        store.append(store_data["address"]["streetAddress"])
        store.append(store_data["address"]["addressLocality"])
        store.append(store_data["address"]["addressRegion"])
        store.append(store_data["address"]["postalCode"])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["telephone"])
        store.append("district taco")
        store.append(geo_locations[i][0])
        store.append(geo_locations[i][1])
        store.append(" ".join(store_data["openingHours"]))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
