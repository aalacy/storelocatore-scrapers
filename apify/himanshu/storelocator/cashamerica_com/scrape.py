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
    base_url = "http://cashamerica.com/"
    r = session.get("http://find.cashamerica.us/api/stores?p=1&s=10&lat=32.72&lng=-97.45&d=2019-07-20T12:44:39.578Z&key=D21BFED01A40402BADC9B931165432CD").json()
    return_main_object = []
    for val in r:
        store = []
        store.append(base_url)
        store.append(val['shortName'])
        store.append(val['address']['address1'])
        store.append(val['address']['city'])
        store.append(val['address']['state'])
        store.append(val['address']['zipCode'])
        store.append('US')
        store.append(val['storeNumber'])
        store.append(val['phone'])
        store.append("cashamerica")
        store.append(val['latitude'])
        store.append(val['longitude'])
        store.append(val['hours']['displayText'])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
