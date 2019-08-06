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
    base_url = "https://www.snappysalads.com"
    r = requests.get("https://www.snappysalads.com/hours-and-locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all('script'):
        if "document.addEventListener" in script.text:
            data = json.loads(script.text.split("locations:")[1].split("}}}],")[0] + "}}}]")
            for i in range(len(data)):
                store_data = data[i]
                store = []
                store.append("https://www.snappysalads.com")
                store.append(store_data["name"])
                store.append(store_data["street"])
                store.append(store_data["city"])
                store.append(store_data["state"])
                store.append(store_data["postal_code"])
                store.append("US")
                store.append(store_data["id"])
                store.append(store_data["phone_number"].split("(")[0] if store_data["phone_number"] != "" else "<MISSING>")
                store.append("snappy salads")
                store.append(store_data["lat"])
                store.append(store_data["lng"])
                store.append(BeautifulSoup(store_data["hours"],"lxml").get_text().split('“')[0].split('"')[0])
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
