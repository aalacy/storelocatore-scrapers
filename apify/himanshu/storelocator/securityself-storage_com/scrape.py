# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('securityself-storage_com')






session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    # search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    # search.initialize(include_canadian_fsas = True)
    # MAX_RESULTS = 50
    # MAX_DISTANCE = 10
    # current_results_len = 0     # need to update with no of count.
    # zip_code = search.next_zip()


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }


    base_url = "https://www.securityself-storage.com/"

    location_url = "https://inventory.g5marketingcloud.com/api/v1/locations?category_id=4418748%2C3235631&client_id=606%2C718&geosearch=true&page=1&per_page=50&search_radius=50&wildcard=89025"
    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    k = (soup.text)
    m = json.loads(k)
    for g in m['locations']:
        street_address = (g['street'])
        city = (g['city'])
        state = (g['state'])
        zipp  = (g['postal_code'])
        store_number = (g['id'])
        longitude = (g['longitude'])
        latitude = (g['latitude'])
        phone = (g['phone_number'])
        location_name = (g['name'])
        # page_url1 = (g['location_url'])
        # logger.info(page_url1)
        store = []
        store.append("https://www.securityself-storage.com/")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append(store_number if store_number else "<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("Store")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append("https://www.securityself-storage.com/locations#/locations?page=1&wildcard=89025")
        # logger.info(store)
        yield store
        if store[2] in addresses:
            continue
        addresses.append(store[2])
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
