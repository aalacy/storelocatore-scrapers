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
    base_url = "https://vivachicken.com"
    r = session.get("https://vivachicken.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=60058472b8&load_all=1&layout=1").json()
    return_main_object = []
    for loc in r:
        hour=loc['open_hours'].replace('[','').replace(']','').replace('{','').replace('}','')
        hour=hour.replace('\"','')
        store=[]
        store.append(base_url)
        store.append(loc['title'])
        store.append(loc['street'])
        store.append(loc['city'])
        store.append(loc['state'])
        store.append(loc['postal_code'])
        if loc['country']=="United States":
            store.append("US")
        else:
            store.append(loc['country'])
        store.append(loc['id'])
        store.append(loc['phone'])
        store.append("vivachicken")
        store.append(loc['lat'])
        store.append(loc['lng'])
        if hour.strip():
            store.append(hour.strip())
        else:
            store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
