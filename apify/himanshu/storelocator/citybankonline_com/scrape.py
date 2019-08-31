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
    base_url = "https://www.city.bank"
    r = requests.get("https://www.city.bank/Custom/Widgets/CityBankMap/BankLocations.ashx?tag=",headers=headers)
    address_reqeust = requests.get("https://www.city.bank/locations","lxml")
    address_soup = BeautifulSoup(address_reqeust.text,"lxml")
    data = r.json()
    return_main_object = []
    for store_data in data:
        hours = " ".join(list(BeautifulSoup(store_data["Description"].replace("&lt;","<").replace("&gt;",">"),"lxml").stripped_strings))
        for p in address_soup.find_all("p"):
            if store_data["Street"] in p.text:
                if store_data["Street"] in list(p.stripped_strings)[0] and store_data["Street"] != list(p.stripped_strings)[0]:
                    store_data["Street"] = list(p.stripped_strings)[0]
        store = []
        store.append("https://citybankonline.com")
        store.append(store_data['Title'])
        store.append(store_data["Street"])
        store.append(store_data['City'])
        store.append(store_data['StateCode'])
        store.append(store_data["Zip"])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["PhoneNumber"])
        store.append("city bank")
        store.append(store_data["Latitude"])
        store.append(store_data["Longitude"])
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
