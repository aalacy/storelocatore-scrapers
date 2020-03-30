
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addressess = []

    headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    }
    base_url = "http://www.ntw.com"
    location_url = "http://www.ntw.com/Content/json/ntw-locations.json"
    r = session.get(location_url, headers=headers).json()
    for i in r :
        street_address = (i['Address'])
        city = (i['City'])
        state = (i['State'])
        zipp = (i['Zip'])
        phone  =(i['Phone'])
        latitude = (i['Latitude'])
        longitude = (i['Longitude'])
        locator_domain = base_url
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append('<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append('<MISSING>' )
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
