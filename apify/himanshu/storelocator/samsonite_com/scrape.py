import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


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
    base_url = "https://www.samsonite.com"
    r = session.get("https://shop.samsonite.com/on/demandware.store/Sites-samsonite-Site/default/Stores-GetNearestStores?postalCode=11756&distanceUnit=mi&maxdistance=150000000&maxResults=10000")
    data = r.json()["stores"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.samsonite.com")
        store.append(store_data['name'])
        store.append(store_data["address1"] + store_data["address2"] if "address2" in store_data else store_data["address1"])
        if store[-1] == "":
            store[-1] = "<MISSSING>"
        store.append(store_data['city'] if store_data["city"] != "" else "<MISSING>")
        store.append(store_data['stateCode'] if store_data['stateCode'] != "" else "<MISSING>")
        store.append(store_data['postalCode'])
        store.append(store_data["countryCode"] if store_data["countryCode"] != "" else "US")
        store.append(store_data["storeid"])
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append("samsonite " + store_data["storeType"])
        store.append(store_data['latitude'])
        store.append(store_data['longitude'])
        store.append(BeautifulSoup(store_data["storeHours"],"lxml").get_text() if store_data['storeHours'] != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
