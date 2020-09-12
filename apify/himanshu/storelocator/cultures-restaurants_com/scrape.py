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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://storerocket.global.ssl.fastly.net/api/user/0kDJ39Qpmn/locations?radius=20"
    r = session.get(base_url).json()['results']['locations']
    return_main_object = []
    for i in range(len(r)):
        store = []
        store.append("https://cultures-restaurants.com")
        store.append(base_url)
        store.append(r[i]['name'])
        store.append((r[i]['address_line_1'].strip() + " " + r[i]['address_line_2'].strip()).strip())
        store.append(r[i]['city'])
        store.append(r[i]['state'].strip())
        if r[i]['postcode']!="":
            store.append(r[i]['postcode'])
        else:
            store.append("<MISSING>")
        store.append(r[i]['country'])
        store.append(r[i]['id'])
        store.append(r[i]['phone'])
        store.append("<MISSING>")
        store.append(r[i]['lat'])
        store.append(r[i]['lng'])
        hours = json.dumps(r[i]['hours']).replace("null","closed").replace('"',"").replace(",","")[1:-1]
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
