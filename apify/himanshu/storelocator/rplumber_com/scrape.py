import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.rplumber.com"
    r = session.get("https://api.rplumber.com/locations").json()
    return_main_object = []
    for loc in r['data']:
        store=[]
        hour=json.dumps(loc['hours']).strip('{}')
        store.append(base_url)
        store.append("<MISSING>")
        store.append(loc['address'].strip())
        store.append(loc['city'].strip())
        store.append(loc['state'].strip())
        store.append(loc['zip'])
        store.append("US")
        if loc['store_id']:
            store.append(loc['store_id'])
        else:
            store.append("<MISSING>")
        if loc['phone']:
            store.append(loc['phone'])
        else:
            store.append("<MISSING>")
        store.append("rplumber")
        store.append(loc['latitude'])
        store.append(loc['longitude'])
        store.append(hour)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
