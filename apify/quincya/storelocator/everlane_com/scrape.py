import csv
import json
import time
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

    base_link = "https://www.everlane.com/api/v2/storefronts"

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)

    base = BeautifulSoup(req.text,"lxml")
    stores = json.loads(base.text.strip())["storefronts"]

    data = []
    locator_domain = "everlane.com"

    for store in stores:
        location_name = "Everlane - " + store["name"]
        street_address = store["street_address"]
        city = store['city']
        state = store["region_code"]
        zip_code = store["postal_code"]
        if len(zip_code) < 5:
            zip_code = "<MISSING>"
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store['phone']
        hours_of_operation = store["hours"].replace("\n", " ")
        latitude = store['latitude']
        longitude = store['longitude']
        link = "https://www.everlane.com/stores/" + store["name"].lower().replace(" ","-")
        if "," in link:
            link = link[:link.find(",")].strip()
        if street_address == "Stanford Shopping Center":
            link = "https://www.everlane.com/stores/stanford-shopping-center"

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
