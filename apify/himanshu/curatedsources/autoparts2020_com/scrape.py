import csv
import requests
from bs4 import BeautifulSoup
import re
import json
requests.packages.urllib3.disable_warnings()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://autoparts2020.com"
    r = requests.get("https://autoparts2020.com/locations/locator/?distance=100000&partStore=true&query=90002&serviceDealer=false",headers=headers,verify=False)
    data = r.json()["hits"]
    return_main_object = []
    for store_data in data:
        store = []
        store.append("https://autoparts2020.com")
        store.append(store_data["businessName"])
        store.append(store_data["address"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["postalCode"])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["phoneNumber"])
        store.append("auto value" + store_data["businessType"])
        store.append(store_data['latitude'])
        store.append(store_data['longitude'])
        store.append(store_data["businessHoursSummaryString"] if store_data["businessHoursSummaryString"] != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
