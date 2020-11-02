import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata


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
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://volvo.ca"
    r = session.get("https://www.volvocars.com/data/dealers?marketSegment=%2Fen-ca&expand=Services%2CUrls&format=json&northToSouthSearch=False&filter=MarketId+eq+%27ca%27+and+LanguageId+eq+%27en%27&sc_site=en-ca",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    location_url = []
    for store_data in r.json():
        store = []
        store.append("https://volvo.ca")
        store.append(store_data["Name"])
        if len(store_data["AddressLine1"].split(",")) == 1:
            store.append(store_data["AddressLine1"])
        elif len(store_data["AddressLine1"].split(",")) == 2:
            store.append(store_data["AddressLine1"].split(",")[0])
        else:
            store.append(",".join(store_data["AddressLine1"].split(",")[:-2]))
        store.append(store_data["City"])
        store.append(store_data["District"])
        store.append(store_data["ZipCode"])
        store.append("CA")
        store.append(store_data["VccDealerId"])
        store.append(store_data["Phone"] if store_data["Phone"] else "<MISSING>")
        store.append("<MISSING>")
        store.append(store_data["GeoCode"]["Latitude"])
        store.append(store_data["GeoCode"]["Longitude"])
        store.append("<MISSING>")
        store.append(store_data["Url"] if store_data["Url"] else "<MISSING>")
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
