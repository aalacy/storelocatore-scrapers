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
    base_url = "https://www.saksoff5th.com"
    r = session.get("http://locations.saksoff5th.com/en/api/v2/stores.json").json()
    return_main_object = []
    for data in r['stores']:
        hour=''
        for hr in data['regular_hour_ranges']:
            hour+=hr['days']+":"+hr['hours']+' '
        store=[]
        store.append(base_url)
        store.append(data['name'].strip())
        store.append(data['address_1'].strip())
        store.append(data['city'].strip())
        store.append(data['state'].strip())
        store.append(data['postal_code'].strip())
        store.append(data['country_code'].strip())
        store.append(data['number'].strip())
        store.append(data['phone_number'].strip())
        store.append("saksoff5th")
        store.append(data['latitude'])
        store.append(data['longitude'])
        if hour:
            store.append(hour.strip())
        else:
            store.append("<MISSING>")    
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
