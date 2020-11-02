import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jysk_ca')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.jysk.ca"
    url = "https://www.jysk.ca/storelocator/ajax/stores/?_=1600683863752"
    response = session.get(url).json()
    for current_store in response:
        store = []
        store.append("https://www.jysk.ca")
        store.append(current_store["name"])
        store.append(bs(current_store["address"],"lxml").text)
        store.append(current_store["city"])
        store.append(current_store["region"])
        store.append(current_store["postcode"])
        if current_store['country_id'] != "CA":
            continue
        store.append(current_store["country_id"])  
        store.append(current_store["legacy_warehouse_id"])
        store.append(current_store["phone"] if current_store["phone"] != None else "<MISSING>")
        store.append("<MISSING>")
        store.append(current_store["latitude"])
        store.append(current_store["longitude"])
        hours = " ".join(list(bs(current_store["schedule"],"lxml").stripped_strings)).replace("New Calgary JYSK location coming soon!","")
        store.append(hours.strip().lstrip() if hours.strip().lstrip() != "" else "<MISSING>")
        store.append("<MISSING>")
        yield store
        # logger.info(hours)



def scrape():
    data = fetch_data()
    write_output(data)

scrape()
