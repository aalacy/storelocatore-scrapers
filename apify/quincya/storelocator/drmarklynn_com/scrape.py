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

    data = []
    found_poi = []

    locator_domain = "drmarklynn.com"

    base_link = "https://drmarklynn.com/wp-json/wp/v2/location?page=1&per_page=100&_embed"

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)

    base = BeautifulSoup(req.text,"lxml")
    stores = json.loads(base.text.strip())

    for i in stores:
        store = i["acf"]
        location_name = store['location_address_map']['name']
        raw_address = store["location_address_map"]["address"]
        street_address = (raw_address["line_1"] + " " + raw_address["line_2"]).strip()
        city = raw_address['city']
        state = raw_address["state"]
        zip_code = raw_address["zip"]
        country_code = "US"
        store_number = store["location_office_number"]
        location_type = "<MISSING>"
        phone = store['location_address_map']['info']['phone']
        hours_of_operation = "<MISSING>"
        latitude = store['location_address_map']['position']['lat']
        longitude = store['location_address_map']['position']['lng']

        if store_number not in found_poi:
            # Store data
            data.append([locator_domain, "<MISSING>", location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
            found_poi.append(store_number)

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
