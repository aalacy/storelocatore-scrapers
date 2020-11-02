import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []
    for zip_code in zips:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
            "Content-Type":"application/json;charset=UTF-8"
        }
        base_url = "https://www.valleynationalbank.com"
        data = '{"Location":"' + str(zip_code) + '"}'
        r = session.post("https://www.valley.com/siteAPI/Branch/Branches",headers=headers,data=data)
        r_data = r.json()
        if type(r_data) != dict:
            r_data = json.loads(r.json())
        if "Message" in r_data:
            continue
        for store_data in r_data["Branches"]:
            if store_data["StreetAddress"] in addresses:
                continue
            addresses.append(store_data["StreetAddress"])
            location_request = session.get("https://www.valley.com/" + store_data["Path"])
            location_soup = BeautifulSoup(location_request.text,"lxml")
            hours = " ".join(list(location_soup.find("div",{'class':"columns small-12 medium-7 large-4 panel--column"}).stripped_strings))
            store = []
            store.append("https://www.valleynationalbank.com")
            store.append(store_data["Name"])
            store.append(store_data["StreetAddress"])
            store.append(store_data["City"])
            store.append(store_data["State"])
            store.append(store_data["Zipcode"] if store_data["Zipcode"] != "" else "<MISSING>")
            store.append("US")
            store.append(store_data["ID"] if store_data["ID"] != "" else "<MISSING>")
            store.append(store_data["PhoneFormatted"] if store_data["PhoneFormatted"] != "" else "<MISSING>")
            store.append("valley " + store_data["Type"])
            store.append(store_data["Lat"])
            store.append(store_data["Lng"])
            store.append(hours)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()