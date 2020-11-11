import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    }
    r = session.get("https://shop.samsonite.com/on/demandware.store/Sites-samsonite-Site/default/Stores-GetNearestStores?postalCode=11756&distanceUnit=mi&maxdistance=150000000&maxResults=10000", headers=headers)
    data = r.json()["stores"]
    
    for i in range(len(data)):
        store_data = data[i]
        if "Permanently Closed" in store_data["storeHours"]:
            continue
        street_address = (store_data['address1'] +" "+ str(store_data['address2'])).replace(",","").strip()
        # if "-" in street_address:
        #     street_address = street_address.split("-")[1]
        store = []
        store.append("https://www.samsonite.com")
        store.append(store_data['name'])
        store.append(street_address)
        store.append(store_data['city'] if store_data["city"] != "" else "<MISSING>")
        store.append(store_data['stateCode'] if store_data['stateCode'] != "" else "<MISSING>")
        store.append(store_data['postalCode'])
        store.append("US" if store_data["postalCode"].replace("-","").isdigit() else "CA")
        store.append(store_data["storeid"])
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append("Samsonite")
        store.append(store_data['latitude'])
        store.append(store_data['longitude'])
        store.append(" ".join(list(BeautifulSoup(store_data["storeHours"],"lxml").stripped_strings)).replace("Temporarily Closed","<MISSING>").replace("Opened with Reduced Hours","") if store_data['storeHours'] != "" else "<MISSING>")
        store.append("https://shop.samsonite.com/on/demandware.store/Sites-samsonite-Site/default/Stores-Details?StoreID="+str(store_data["storeid"]))
        store = [str(x).strip() if x else "<MISSING>" for x in store]

        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
