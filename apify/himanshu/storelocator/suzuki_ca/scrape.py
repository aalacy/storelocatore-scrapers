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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    data = 'ajax=1&action=get_nearby_stores&distance=100000&suzukitype=matv&storetype=undefined&lat=43.7086666&lng=-79.30808809999996'
    base_url = "https://www.suzuki.ca"
    r = session.post("https://www.suzuki.ca/mapsearch/index_matvmarine.php",headers=headers,data=data,verify=False)
    return_main_object = []
    location_data = r.json()['stores']
    for store_data in location_data:
        store = []
        store.append("https://www.suzuki.ca")
        store.append(store_data["name"])
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("CA")
        store.append(store_data["dealernumber"])
        store.append(store_data["telephone"])
        store.append("suzuki")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append("<MISSING>")
        store.append(store_data["address"])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
