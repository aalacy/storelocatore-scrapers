import csv
import os
from sgselenium import SgSelenium
import usaddress
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_addy(addy):

    parsed_add = usaddress.tag(addy)[0]

    street_address = ''

    if 'AddressNumber' in parsed_add:
        street_address += parsed_add['AddressNumber'] + ' '
    if 'StreetNamePreDirectional' in parsed_add:
        street_address += parsed_add['StreetNamePreDirectional'] + ' '
    if 'StreetNamePreType' in parsed_add:
            street_address += parsed_add['StreetNamePreType'] + ' '
    if 'StreetName' in parsed_add:
        street_address += parsed_add['StreetName'] + ' '
    if 'StreetNamePostType' in parsed_add:
        street_address += parsed_add['StreetNamePostType'] + ' '
    if 'OccupancyType' in parsed_add:
        street_address += parsed_add['OccupancyType'] + ' '
    if 'OccupancyIdentifier' in parsed_add:
        street_address += parsed_add['OccupancyIdentifier'] + ' ' 

    street_address = street_address.strip()
    city = parsed_add['PlaceName'].strip()
    state = parsed_add['StateName'].strip()
    zip_code = parsed_add['ZipCode'].strip()
    
    return street_address, city, state, zip_code

def fetch_data():
    
    locator_domain = 'https://www.mygatestore.com/'
    ext = 'find-a-gate/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    driver.implicitly_wait(30)
    time.sleep(5)

    locs = driver.find_elements_by_css_selector('div.store-locator__infobox')
    all_store_data = []
    for loc in locs:
        location_name = loc.find_element_by_css_selector('div.store-location').text.strip()
        if location_name == '':
            continue
        
        store_number = location_name.split('#')[1]
        
        raw_addy = loc.find_element_by_css_selector('div.store-address').text
        if 'USA' not in raw_addy:
            addy = raw_addy
        else:
            addy_1 = raw_addy.split(',')[0]
            addy_2 = raw_addy.split('USA')[1]
            addy = addy_1 + addy_2
        
        if '26699 FL 56' in addy_1:
            street_address = '26699 FL 56'
            city = 'Wesley Chapel'
            state = 'FL'
            zip_code = '33544'
        else:
            street_address, city, state, zip_code = parse_addy(addy)
        
        maps_href = loc.find_element_by_css_selector('a.infobox__row.infobox__cta.ssflinks').get_attribute('href')
        start = maps_href.find('(')
        coords = maps_href[start + 1: -1].split(',%20')
        
        lat = coords[0]
        longit = coords[1]
        
        country_code = 'US'

        location_type = '<MISSING>'
        page_url = '<MISSING>'
        phone_number = '<MISSING>'
        hours = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
