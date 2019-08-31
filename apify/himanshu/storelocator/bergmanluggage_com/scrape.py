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
    base_url = "https://bergmanluggage.com"
    r = requests.get("https://bergmanluggage.com/pages/all-store-locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    data = json.loads(soup.find("div",{"develic-map":re.compile('{')})["develic-map"])["items"]
    for i in range(len(data)):
        store_data = data[i]
        address = list(BeautifulSoup(store_data["b"],"lxml").stripped_strings)
        store = []
        store.append("https://bergmanluggage.com")
        store.append(store_data["t"])
        store.append(" ".join(address[0].split(",")[0:-3]))
        store.append(address[0].split(",")[-3])
        store.append(address[0].split(",")[-2].split(" ")[-2])
        store.append(address[0].split(",")[-2].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(address[1] if len(address) == 2 else "<MISSING>")
        store.append("bergman luggage")
        store.append(store_data["lt"])
        store.append(store_data["lg"])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
