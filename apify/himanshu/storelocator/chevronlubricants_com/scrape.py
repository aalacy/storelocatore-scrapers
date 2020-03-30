import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    return_main_object = []
    addresses = []
    store_cords = []
    cords = sgzip.coords_for_radius(100)
    for cord in cords:
        base_url = "https://www.chevronlubricants.com"
        r = session.get("https://locators.deloperformance.com/api/ws_marketerLocator-search-geo.aspx?lat=" + str(cord[0]) + "&lng=" + str(cord[1]) + "&radius=100&output=json&zoom=12&region=us&v=2",headers=headers,verify=False)
        data = r.json()["marketers"]
        for store_data in data:
            store = []
            store.append("https://www.chevronlubricants.com")
            store.append(store_data["accountName"])
            store.append(store_data["address"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["city"])
            store.append(store_data["state"])
            store.append(store_data["postal_code"] if store_data["postal_code"] else "<MISSING>")
            if store[-1].replace("-","").isdigit() == False:
                continue
            store.append("US")
            store.append(store_data["id"])
            store.append(store_data["phone"] if store_data["phone"] else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["lat"])
            store.append(store_data["lng"])
            if [store[-2],store[-1]] in store_cords:
                continue
            store_cords.append([store[-2],store[-1]])
            store.append("<MISSING>")
            store.append("<MISSING>")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()