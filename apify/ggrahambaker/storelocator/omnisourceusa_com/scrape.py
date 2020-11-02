import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
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
    locator_domain = 'https://www.omnisourceusa.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    coords = driver.execute_script('return omniLocations')

    addys = driver.find_elements_by_css_selector('address.mb-3')
    all_store_data = []
    for addy in addys:
        cont = addy.text.split('\n')
        location_name = cont[0]

        street_address = cont[1].replace(',', '')

        if len(cont) == 6:
            street_address += ' ' + cont[2]
            off = 1
        else:
            off = 0
        city, state, zip_code = addy_ext(cont[off + 2])

        phone_number = cont[off + 3].replace('Phone:', '').strip()

        for coord in coords:
            if coord['name'] == location_name:
                lat = coord['lat']
                longit = coord['lng']

        country_code = 'US'
        page_url = '<MISSING>'
        hours = '<MISSING>'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
