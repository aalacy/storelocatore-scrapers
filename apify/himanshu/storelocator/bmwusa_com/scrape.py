import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from datetime import datetime


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    zips = sgzip.for_radius(200)
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    for zip_code in zips:
        #print("zip_code === "+zip_code)
        base_url = "https://www.bmwusa.com"
        r = session.get("https://www.bmwusa.com/api/dealers/" + str(zip_code) + "/1000",headers=headers)
        for store_data in r.json()["Dealers"]:
            store = []
            store.append("https://www.bmwusa.com")
            store.append(store_data["DefaultService"]["Name"])
            store.append(store_data["DefaultService"]["Address"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["DefaultService"]["City"])
            store.append(store_data["DefaultService"]["State"])
            store.append(store_data["DefaultService"]["ZipCode"])
            store.append("US")
            store.append(store_data["CenterId"])
            store.append(store_data["DefaultService"]["FormattedPhone"] if store_data["DefaultService"]["FormattedPhone"] != "" and store_data["DefaultService"]["FormattedPhone"] != None else "<MISSING>")
            store.append("bmw")
            store.append(store_data["DefaultService"]["LonLat"]["Lat"])
            store.append(store_data["DefaultService"]["LonLat"]["Lon"])
            hours = " ".join(list(BeautifulSoup(store_data["DefaultService"]["FormattedHours"],"lxml").stripped_strings))
            store.append(hours if hours != "" else "<MISSING>")
            store.append("<MISSING>")

            return_main_object.append(store)
        return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
