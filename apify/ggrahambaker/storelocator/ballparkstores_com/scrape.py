import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code

def fetch_data():
    # Your scraper here

    locator_domain = 'http://ballparkstores.com/'
    ext = 'locations.htm'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    table = driver.find_element_by_css_selector('table.viewmap')
    rows = table.find_elements_by_css_selector('tr')
    all_store_data = []
    for row in rows:
        cols = row.find_elements_by_css_selector('td')
        for col in cols:
            content = col.text.split('\n')
            if len(content) == 5:
                address = content[0].split('#28 ')
                street_address = address[1].strip()

                store_number = '28'
                location_name = 'BALLPARK Store #28'
                city, state, zip_code = addy_extractor(content[1])
                phone_number = content[2]
            elif len(content) == 6 or len(content) == 7:
                idx = content[0].find('#')
                location_name = content[0]
                store_number = content[0][idx + 1:idx + 3]

                street_address = content[1]
                city, state, zip_code = addy_extractor(content[2])
                phone_number = content[3]
            else:
                continue

            country_code = 'US'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
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
