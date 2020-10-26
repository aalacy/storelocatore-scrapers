import csv
import os
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('instyprints_com')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.instyprints.com/'
    ext = 'instyprints/frontend/locationsMap.js'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200

    content = page.text.split("var franchiseeLocations =")[1].split("var youAreHereLat")[0].strip()
    store_data = json.loads(content[:-1])

    all_store_data = []
    for store in store_data:
        location_name = store['LocationName']
        street_address = (store['Line1'] + " " + store['Line2']).strip()
        city = store['City']
        state = store['State']
        zip_code = store['Postal']
        phone_number = store['PhoneWithCountryCode']
        lat = store['Latitude']
        longit = store['Longitude']
        country_code = 'US'
        location_type = '<MISSING>'
        store_number = store['LocationNumber']

        page_url = store['MicroSiteUrl']

        page = session.get(page_url)
        base = BeautifulSoup(page.text,"lxml")
        hours = base.find(class_="oprationalHours").text.replace("Hours of Operation","").replace("Days Hours","").replace("Add custom operation hours","Closed")
        hours = (re.sub(' +', ' ', hours)).strip()
        if not hours:
            hours = '<MISSING>'

        if "eden-prairie-mn" in page_url:
            phone_number = "612-254-6416"
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        # logger.info(store_data)
        # logger.info()
        all_store_data.append(store_data)
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
