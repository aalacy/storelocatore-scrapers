import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    r = requests.get("https://www.caesars.com/harrahs",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all("option",{'data-type':"PROPERTY"}):
        try:
            location_request = requests.get("https://www.caesars.com/api/v1/properties/" + location["data-propcode"],headers=headers)
            store_data = location_request.json()
        except:
            continue
        address = store_data["address"]
        store = []
        store.append("https://www.harrahs.com")
        store.append(store_data["name"])
        store.append(address["street"])
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])
        if "," in address["city"]:
            store.append(address["city"].split(",")[0])
            store.append(address["city"].split(",")[1])
            store.append(address["zip"])
            store.append("CA")
        else:
            store.append(address["city"])
            store.append(address["state"])
            store.append(address["zip"])
            store.append("US")
        store.append(store_data["preferenceId"])
        store.append(store_data["phone"].replace("SHOE","") if store_data["phone"] else "<MISSING>")
        store.append("<MISSING>")
        store.append(store_data["location"]["latitude"])
        store.append(store_data["location"]["longitude"])
        hours = "<MISSING>"
        store.append(hours if hours else "<MISSING>")
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()