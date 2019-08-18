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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    "Content-Type": "application/json; charset=UTF-8"
    }
    base_url = "https://racetrac.com"
    data = '{"swLat":19.56371046529199,"swLng":-154.56903,"neLat":41.7744145203491,"neLng":-45.584655,"features":[]}'
    r = requests.post("https://racetrac.com/Services.asmx/Locate",headers=headers,data=data)
    return_main_object = []
    location_list = r.json()
    for key in location_list:
        if "Stores" in location_list[key]:
            for store_data in location_list[key]["Stores"]:
                store = []
                store.append("https://racetrac.com")
                store.append(store_data['Address'])
                store.append(store_data["Address"])
                store.append(store_data['City'])
                store.append(store_data['State'])
                store.append(store_data["ZipCode"])
                store.append("US")
                store.append(store_data["ID"])
                store.append(store_data["PhoneNumber"] if store_data["PhoneNumber"] != "" else "<MISSING>")
                store.append("race trac")
                store.append(store_data["Latitude"])
                store.append(store_data["Longitude"])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
