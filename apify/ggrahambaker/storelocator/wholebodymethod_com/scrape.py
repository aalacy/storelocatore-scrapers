import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.wholebodymethod.com/'
    ext = 'location'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    all_store_data = []
    locs = driver.find_elements_by_css_selector('div.sqs-block-content')
    for loc in locs:
        cont = loc.text.split('\n')

        if len(cont) < 8:
            continue

        location_name = cont[0]

        street_address = cont[1]

        city, state, zip_code = addy_ext(cont[2])

        phone_number = cont[3]

        hours = ''
        for h in cont[4:]:
            if 'Virtual' in h:
                break
            hours += h + ' '

        hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain,'https://www.wholebodymethod.com/location', location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
