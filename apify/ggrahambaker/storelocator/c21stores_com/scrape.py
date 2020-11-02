import csv
import os
from sgselenium import SgSelenium
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.c21stores.com/'
    ext = 'stores'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    divs = driver.find_elements_by_css_selector('div.store')
    all_store_data = []

    for div in divs:
        content = div.text.split('\n')
        location_name = content[0]
        parsed_add = usaddress.tag(content[2])[0]

        street_address = ''
        street_address += parsed_add['AddressNumber'] + ' '
        if 'StreetNamePreDirectional' in parsed_add:
            street_address += parsed_add['StreetNamePreDirectional'] + ' '

        street_address += parsed_add['StreetName'] + ' '
        if 'StreetNamePostType' in parsed_add:
            street_address += parsed_add['StreetNamePostType']
        city = parsed_add['PlaceName']
        state = parsed_add['StateName']
        zip_code = parsed_add['ZipCode']

        phone_number = content[3]
        hours = ''
        for h in content[5:-2]:
            hours += h + ' '
        hours = hours.strip()

        link_ref = div.find_elements_by_css_selector('a')[0].get_attribute('href')
        idx = link_ref.find('y=')
        coords = link_ref[idx + 2:].split(',')
        lat = coords[0]
        longit = coords[1]

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
