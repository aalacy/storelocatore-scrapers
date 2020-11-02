import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    r = requests.get("https://www.brewersassociation.org/wp-content/themes/ba2019/json-store/breweries/breweries.json",headers=headers)
    data = json.loads(r.json())["ResultData"]
    addresses = []
    for location in data:
        if location["Address1"] == "":
            continue
        store = []
        store.append("https://www.brewersassociation.org")
        store.append(location["InstituteName"] if location["InstituteName"] else "<MISSING>")
        store.append(location["Address1"] if location["Address1"] else "<MISSING>")
        if store[-1] != "<MISSING>":
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
        store.append(location["City"] if location["City"] else "<MISSING>")
        store.append(location["StateProvince"] if location["StateProvince"] else "<MISSING>")
        store.append(location["Zip"] if location["Zip"] else "<MISSING>")
        if location["Country"] == "Canada":
            store.append("CA")
            store[-2] = store[-2].replace(" ","")
            if store[-2] != "<MISSING>":
                store[-2] = store[-2][:3] + " " + store[-2][3:]
                store[-2] = store[-2].upper()
        elif location["Country"] == "":
            store.append("US")
        else:
            continue
        store.append("<MISSING>")
        store.append(location["WorkPhone"] if location["WorkPhone"] else "<MISSING>")
        store.append(location["BreweryType"] if location["BreweryType"] else "<MISSING>")
        store.append(location["Latitude"] if location["Latitude"] and location["Latitude"] != "0.0000000" else "<MISSING>")
        store.append(location["Longitude"] if location["Longitude"] and location["Longitude"] != "0.0000000" else "<MISSING>")
        store.append("<MISSING>")
        store.append("https://www.brewersassociation.org/directories/breweries/")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()