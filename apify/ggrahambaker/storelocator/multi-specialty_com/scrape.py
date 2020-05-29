import csv
import os
from sgselenium import SgSelenium
import re

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
    locator_domain = 'http://www.multi-specialty.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    map_area = driver.find_element_by_css_selector('map#Map')
    areas = map_area.find_elements_by_css_selector('area')
    link_list = []
    for area in areas:
        link_list.append(area.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        locs = driver.find_elements_by_css_selector('div.map_descrip')
        for loc in locs:
            cufons = loc.find_element_by_css_selector('h6').find_elements_by_css_selector('cufon')
            location_name = ''

            for cuf in cufons:
                location_name += cuf.get_attribute('alt')

            p = re.compile('\d{3}\-\d{3}\-\d{4}')
            for m in p.finditer(loc.text):
                phone_number = m.group()
                cut_idx = m.start()
                break
            p = re.compile('\(\d{3}\)\ \d{3}\-\d{4}')
            for m in p.finditer(loc.text):
                phone_number = m.group()
                cut_idx = m.start()
                break

            addy = loc.text[:cut_idx].replace('\n', ' ')
            addy = addy.replace('The Village Medical Ctr.', '')
            addy = addy.replace('(Sat. Hrs. 9-12)', '')

            parsed_add = usaddress.tag(addy)[0]

            street_address = ''

            if 'AddressNumber' in parsed_add:
                street_address += parsed_add['AddressNumber'] + ' '
            if 'StreetNamePreDirectional' in parsed_add:
                street_address += parsed_add['StreetNamePreDirectional'] + ' '
            if 'StreetName' in parsed_add:
                street_address += parsed_add['StreetName'] + ' '
            if 'StreetNamePostType' in parsed_add:
                street_address += parsed_add['StreetNamePostType'] + ' '
            if 'OccupancyType' in parsed_add:
                street_address += parsed_add['OccupancyType'] + ' '
            if 'OccupancyIdentifier' in parsed_add:
                street_address += parsed_add['OccupancyIdentifier'] + ' '
            city = parsed_add['PlaceName']
            state = parsed_add['StateName']
            zip_code = parsed_add['ZipCode']

            country_code = 'US'
            longit = '<MISSING>'
            lat = '<MISSING>'
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
