import csv
import os
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://tacomaker.com'
    ext = '/donde-estamos'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    loc = driver.execute_script('return tm_locations')

    all_store_data = []
    already_seen = True
    for l in loc:
        soup = BeautifulSoup(l['description'], 'html.parser')
        location_name = soup.find('h1')
        if location_name:
            location_name = location_name.text
        else:
            location_name = '<MISSING>'

        if 'Caracas, Venezuela' in soup.text:
            continue
        if 'Centro Comercial' in soup.text and already_seen:
            already_seen = False
            continue

        addy_raw_first = soup.find('p').text
        if 'Teléfono:' in addy_raw_first:
            phone_number = addy_raw_first[addy_raw_first.find(':') + 1:].split('Fax')[0]
            addy_raw = addy_raw_first.split('Teléfono')[0]
        else:
            addy_raw = addy_raw_first

        zip_code_r = re.search('\d{5}', addy_raw)
        if zip_code_r:
            zip_code = zip_code_r.group(0)
            street_address = addy_raw.replace('PR', '').replace(zip_code, '')

        else:
            zip_code = '<MISSING>'
            street_address = addy_raw.replace('PR', '')

        city = '<MISSING>'
        state = 'PR'

        lat = l['location']['lat']
        longit = l['location']['lng']

        country_code = 'US'
        store_number = '<MISSING>'

        location_type = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
