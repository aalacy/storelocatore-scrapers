import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import time
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    for data in session.get("https://www.pruitthealth.com/bin/pruitthealthlocator").json():
        location_name = data['Title']
        
        if not data['Street']:
            continue
        
        if len(data["Address"].split(",")) > 2:
            street_address = " ".join(data['Address'].split(",")[:-2])
        else:
            street_address = data['Street']
        city = data['City'].replace("Beaufort","Okatie")
        state = data['State']
        zipp = data['Zip'].replace("29902","29909")
        latitude = data['Latitude']
        longitude = data['Longitude']
        store_number = data['ID']
        phone = data['Phone']
        page_url = "http://www.pruitthealth.com/microsite/facilityid" + str(store_number)

        store = []
        store.append("http://www.pruitthealth.com/")
        store.append(location_name)
        store.append(street_address.replace("2051 Elijah Ludd Rd","2051 Elijah Ludd Rd Suite 1").replace("301 Halton Road","301 Halton Road Suite B"))
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(page_url)
        
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
