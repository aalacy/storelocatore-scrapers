import csv
import json
import time
from random import randint
from sgrequests import SgRequests
from bs4 import BeautifulSoup


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    base_link = "https://www.academy.com/api/stores?lat=31.96&lon=-99.90&rad=10000&bopisEnabledFlag=false"
        
    req = session.get(base_link, headers = HEADERS)
    time.sleep(randint(3,4))

    base = BeautifulSoup(req.text,"lxml")
    stores = json.loads(base.text.strip())["stores"]

    data = []
    locator_domain = "academy.com"

    for store in stores:
        location_name = store["properties"]['storeName']
        street_address = store["properties"]['streetAddress']
        city = store["properties"]['city']
        state = store["properties"]["stateCode"]
        zip_code = store["properties"]['zipCode']
        if len(zip_code) < 5:
            zip_code = "<MISSING>"
        country_code = store["properties"]['country']
        store_number = store["storeId"].split("-")[-1]
        location_type = store["properties"]["services"].replace("View details","").strip().replace("\n",",").strip()
        phone = store["properties"]['phone']
        hours_of_operation = store["properties"]['storeHours']
        latitude = store['geometry']['coordinates'][0]
        longitude = store['geometry']['coordinates'][1]

        # Store data
        data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
