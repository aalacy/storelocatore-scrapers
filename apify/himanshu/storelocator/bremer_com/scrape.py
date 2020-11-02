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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.bremer.com"
    r = session.get("https://www.bremer.com/api/locator/search/branches,atms/37.0901202,-95.71336969999999/10000/1/10000",headers=headers)
    data = r.json()["data"]["locationDetailsSearchResponse"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.bremer.com")
        store.append(store_data["title"])
        store.append(store_data["address"]["address1"])
        store.append(store_data["address"]["city"])
        store.append(store_data["address"]["state"])
        store.append(store_data["address"]["zip"])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append("bremer bank")
        store.append(store_data["coordinates"]["latitude"])
        store.append(store_data["coordinates"]["longitude"])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
 




