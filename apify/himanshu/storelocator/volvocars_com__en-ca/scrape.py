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
    headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.volvocars.com/en-ca"
    r = session.get("https://www.volvocars.com/data/dealers?marketSegment=%2Fen-ca&expand=Services%2CUrls&format=json&northToSouthSearch=False&filter=MarketId+eq+%27ca%27+and+LanguageId+eq+%27en%27&sc_site=en-ca",headers=headers)
    return_main_object = []
    location_data = r.json()
    for store_data in location_data:
        store = []
        store.append("https://www.volvocars.com/en-ca")
        store.append(store_data["Name"])
        store.append(store_data["AddressLine1"].split(",")[0])
        store.append(store_data["City"])
        store.append(store_data["District"])
        store.append(store_data["ZipCode"])
        store.append("CA")
        store.append(store_data["DealerId"])
        store.append(store_data["Phone"])
        store.append("volvo")
        store.append(store_data["GeoCode"]["Latitude"])
        store.append(store_data["GeoCode"]["Longitude"])
        store.append("<INACCESSIBLE>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
